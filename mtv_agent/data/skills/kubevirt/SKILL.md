---
name: kubevirt
description: KubeVirt VM operations via kubectl virt or oc virt. Use when the user wants to create, start, stop, console/VNC/SSH into, or inspect VMs on OpenShift/Kubernetes. Output CLI for the user to run — do not execute kubectl/oc yourself unless they ask.
---

## For AI assistants

Do **not** run `kubectl`, `oc`, or `virtctl` in the user’s environment unless they explicitly ask you to execute commands. Give **copy-paste** `bash` blocks, explain placeholders (for example `<vm-name>`, `<namespace>`), and note prerequisites (logged-in cluster context, namespace, installed plugin).

# KubeVirt CLI (`kubectl virt` / `oc virt`)

The `kubectl virt` plugin (OpenShift: `oc virt`) generates and manages KubeVirt `VirtualMachine` resources.

## Install the plugin

Tell the user to install the virt plugin (pick one approach):

```bash
# Krew (recommended)
kubectl krew install virt

# Verify
kubectl virt version
```

On OpenShift, the same plugin is typically available as `oc virt` after installing OpenShift Virtualization.

## Discover flags (user runs locally)

```bash
kubectl virt --help
kubectl virt create vm --help
kubectl virt ssh --help
```

## Instance types and preferences (OpenShift)

Prefer **instance types** and **preferences** over raw `--memory` when the cluster exposes them:

```bash
kubectl get virtualmachineclusterinstancetype
kubectl get virtualmachineclusterpreference
```

Common patterns: `u1.medium` (universal), `fedora` / `rhel.9` / `windows.11.virtio` preferences. With a DataSource that has annotations, `--infer-instancetype` and `--infer-preference` can select sizing automatically.

## List and inspect VMs

```bash
kubectl get vm -A
kubectl get vm -n <namespace>
kubectl describe vm <vm-name> -n <namespace>
kubectl get vmi -n <namespace>
```

## Start, stop, restart

```bash
kubectl virt start <vm-name> -n <namespace>
kubectl virt stop <vm-name> -n <namespace>
kubectl virt restart <vm-name> -n <namespace>
```

## Create a VM (examples)

`kubectl virt create vm` prints YAML to stdout — the user pipes it to `kubectl apply`:

**Registry containerdisk + instance type**

```bash
kubectl virt create vm \
  --name=my-fedora \
  --instancetype=u1.medium \
  --preference=fedora \
  --volume-import=type:registry,url:docker://quay.io/containerdisks/fedora:latest,size:30Gi \
  --user=fedora \
  --ssh-key="$(cat ~/.ssh/id_rsa.pub)" \
  | kubectl apply -f -
```

**Cluster DataSource with inferred sizing**

```bash
kubectl virt create vm \
  --name=my-vm \
  --volume-import=type:ds,src:openshift-virtualization-os-images/fedora,size:30Gi \
  --infer-instancetype --infer-preference \
  --user=fedora \
  --ssh-key="$(cat ~/.ssh/id_rsa.pub)" \
  | kubectl apply -f -
```

**Fallback when no instance types (memory only)**

```bash
kubectl virt create vm \
  --name=my-vm \
  --memory=2Gi \
  --run-strategy=Always \
  --volume-import=type:registry,url:docker://quay.io/containerdisks/fedora:latest,size:30Gi \
  --user=fedora \
  --ssh-key="$(cat ~/.ssh/id_rsa.pub)" \
  | kubectl apply -f -
```

List DataSources (OpenShift golden images):

```bash
kubectl get datasource -n openshift-virtualization-os-images
```

### Storage gotcha

If DataVolumes stay pending with missing access mode / storage class, the cluster may lack a default StorageClass. The user can mark one:

```bash
kubectl get storageclass
kubectl annotate storageclass <name> storageclass.kubernetes.io/is-default-class=true
```

## Console and VNC

```bash
kubectl virt console <vm-name> -n <namespace>
kubectl virt vnc <vm-name> -n <namespace>
```

## SSH (virtctl-style via plugin)

```bash
kubectl virt ssh fedora@<vm-name> -n <namespace>
kubectl virt ssh fedora@<vm-name> -n <namespace> --identity-file=~/.ssh/id_rsa
kubectl virt scp ./local.txt fedora@vmi/<vm-name>:./remote.txt -n <namespace>
```

## Pause, migrate

```bash
kubectl virt pause vm <vm-name> -n <namespace>
kubectl virt unpause vm <vm-name> -n <namespace>
kubectl virt migrate <vm-name> -n <namespace>
```

When unsure of a subcommand, tell the user to run `kubectl virt <command> --help` locally.
