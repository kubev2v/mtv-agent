---
name: govc
description: VMware vSphere automation with govc. Use when the user wants to list inventory, power VMs, clone, snapshot, import OVA, or inspect datastores/hosts on vCenter/ESXi. Output CLI for the user to run — do not execute govc yourself unless they ask.
---

## For AI assistants

Do **not** run `govc` or shell scripts on the user’s machine unless they explicitly ask you to execute commands. Give **copy-paste** `bash` blocks, list required `GOVC_*` environment variables, and explain placeholders (paths, VM names, datacenter).

# govc — vSphere CLI

`govc` is a Go-based CLI for VMware vSphere (govmomi). Useful alongside MTV for source-side checks (VMs, snapshots, datastores) before or during migration.

## Install

Point the user to the official release or package manager they prefer:

```bash
# Example: download release from https://github.com/vmware/govmomi/releases
# Ensure the binary is on PATH as `govc`
govc version
```

## Connection environment (user sets locally)

```bash
export GOVC_URL=vcenter.example.com
export GOVC_USERNAME=administrator@vsphere.local
export GOVC_PASSWORD='...'
export GOVC_INSECURE=true   # only if skipping TLS verify
```

Optional defaults to shorten commands:

```bash
export GOVC_DATACENTER=mydc
export GOVC_DATASTORE=datastore1
export GOVC_NETWORK='VM Network'
export GOVC_RESOURCE_POOL=/mydc/host/mycluster/Resources
```

Verify:

```bash
govc about
govc datacenter.info
```

## Help

```bash
govc -h
govc vm.info -h
```

## Browse inventory

```bash
govc ls
govc ls /<dc>/vm
govc ls -l /<dc>/network
govc find / -type m
govc find / -type m -name 'app-*'
```

## VM lifecycle

**Create**

```bash
govc vm.create -m 4096 -c 2 -g ubuntu64Guest \
  -net.adapter vmxnet3 -disk.controller pvscsi \
  -disk 40GB -ds datastore1 my-vm
```

**Clone**

```bash
govc vm.clone -vm /path/to/template -ds datastore1 new-vm
```

**Power**

```bash
govc vm.power -on=true my-vm
govc vm.power -s=true my-vm
govc vm.power -off=true my-vm
```

**Info and IP**

```bash
govc vm.info my-vm
govc vm.ip -v4 my-vm
```

**Destroy**

```bash
govc vm.destroy my-vm
```

## Snapshots

```bash
govc snapshot.create -vm my-vm before-change
govc snapshot.tree -vm my-vm
govc snapshot.revert -vm my-vm before-change
govc snapshot.remove -vm my-vm before-change
```

## Datastore file operations

```bash
govc datastore.ls -ds datastore1
govc datastore.upload ./file.iso "[datastore1] iso/file.iso"
```

## OVA import (common for appliances)

```bash
govc import.ova -folder=/<dc>/vm/folder ./appliance.ova
```

## Guest operations (VMware Tools)

```bash
govc guest.run -vm my-vm /bin/uname -a
govc guest.upload -vm my-vm ./local.cfg /tmp/local.cfg
```

## JSON for scripting

```bash
govc vm.info -json my-vm
govc find / -type m -json
```

When unsure of flags, tell the user to run `govc <command> -h` locally.
