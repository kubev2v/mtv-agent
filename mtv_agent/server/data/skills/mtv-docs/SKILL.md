---
name: mtv-docs
description: Find Red Hat MTV 2.11 documentation links. Use when the user asks about MTV documentation, how to plan or run migrations, provider setup, troubleshooting, performance tuning, hooks, validation rules, storage/network mapping, VDDK, live migration, or any Migration Toolkit for Virtualization topic.
---

# MTV 2.11 Documentation Guide

Use this TOC to suggest the most relevant documentation link when a user asks about MTV topics.
Always link to the specific section using a deep link (Base URL + `#anchor`), not just the chapter.

## How to construct deep links

Red Hat single-page HTML docs use fragment anchors to point to specific sections.
Build a deep link by appending `#<anchor_id>` to the base URL of the guide:

```
<base_url>#<anchor_id>
```

Example — link to the section on creating a VDDK image:

```
https://docs.redhat.com/en/documentation/migration_toolkit_for_virtualization/2.11/html-single/planning_your_migration_to_red_hat_openshift_virtualization/index#creating-vddk-image_mtv
```

When answering a user question, pick the most specific anchor that matches the topic and present it as a clickable markdown link.

## Planning Guide

**Base URL:** `https://docs.redhat.com/en/documentation/migration_toolkit_for_virtualization/2.11/html-single/planning_your_migration_to_red_hat_openshift_virtualization/index`

### Chapter / section anchor reference

| Ch. | Section | Anchor ID | Description |
|-----|---------|-----------|-------------|
| 1 | Planning a migration | `con_planning-intro_mtv` | Overview of supported source providers and migration types |
| 1.1 | Types of migration | `types_of_migration` | Cold, warm, and live migration types |
| 2 | Cold and warm migration | `assembly_cold-warm-migration_mtv` | Differences between cold and warm migration |
| 2.1 | About cold and warm migration | `about-cold-warm-migration_mtv` | Choose cold or warm based on workload |
| 2.1.1 | Cold migration | `cold-migration_mtv` | Default migration type, VMs shut down during copy |
| 2.1.2 | Warm migration | `warm-migration_mtv` | Precopy while VMs run, cutover with minimal downtime |
| 2.2 | Warm migration stages | `warm-migration-stages_mtv` | Precopy and cutover stages overview |
| 2.2.1 | Precopy stage | `precopy_stage` | CBT snapshots at hourly intervals |
| 2.2.2 | Cutover stage | `cutover_stage` | VMs shut down, remaining data migrated |
| 2.3 | Migration speed comparison | `mtv-migration-speed-comparison_mtv` | Speed comparison of cold and warm |
| 2.4 | Choosing a migration type | `choosing-migration-type_mtv` | Decision guide table for cold vs warm |
| 3 | Live migration | `assembly_live-migration_mtv` | GA, OCP Virt ↔ OCP Virt clusters |
| 3.1 | Benefits of live migration | `benefits-live-migration_mtv` | Day 2 ops, minimal downtime |
| 3.2 | Live migration, MTV, and OCP Virt | `live-migration-mtv-cnv_mtv` | Orchestration split between MTV and KubeVirt |
| 3.3 | Limitations of live migration | `live-migration-limitations_mtv` | OCP Virt only, no cross-provider |
| 3.4 | Live migration workflow | `live-migration-workflow_mtv` | Step-by-step lifecycle |
| 4 | Software requirements | `assembly_software-requirements-for-migration_mtv` | Storage, network, VM prerequisites |
| 4.1 | Storage support / default modes | `about-storage_mtv` | Volume and access modes per provisioner |
| 4.2 | Network prerequisites | `network-prerequisites_mtv` | IP/VLAN, reliability, NADs |
| 4.2.1 | Ports | `ports_mtv` | Firewall port tables per provider |
| 4.3 | Source VM prerequisites | `ref_source-vm-prerequisites_mtv` | ISO unmounted, IPv4/IPv6, supported OS |
| 4.4 | Source VM migration considerations | `ref_source-vm-migration-considerations_mtv` | DNS naming, Windows VSS, Secure Boot |
| 4.5 | MTV encryption support | `encryption-support_mtv` | LUKS and BitLocker support |
| 5 | Provider-specific requirements | `assembly_provider-specific-requirements-for-migration_mtv` | Per-provider prereqs |
| 5.1 | RHV prerequisites | `rhv-prerequisites_mtv` | UserRole, ReadOnlyAdmin, LUN disks |
| 5.2 | OpenStack prerequisites | `openstack-prerequisites_mtv` | Token and app-credential auth |
| 5.2.1 | OpenStack token auth | `openstack-token-authentication_mtv` | Token with user ID or user name |
| 5.2.2 | OpenStack app credential auth | `openstack-application-credential-authentication_mtv` | App credential ID or name |
| 5.3 | VMware prerequisites | `vmware-prerequisites_mtv` | VDDK, CBT, NFC, privileges |
| 5.3.1 | VMware privileges | `vmware-privileges_mtv` | Minimum vSphere privilege table |
| 5.3.2 | Creating VMware role | `creating-vmware-role-mtv-permissions_mtv` | Apply MTV privileges in vCenter |
| 5.3.3 | Creating VDDK image | `creating-vddk-image_mtv` | Build and push VDDK init image |
| 5.3.4 | Increasing NFC memory | `increasing-nfc-memory-vmware-host_mtv` | Required for >10 VMs per ESXi host |
| 5.3.5 | VDDK validator containers | `vddk-validator-containers_mtv` | Resource quotas for VDDK pods |
| 5.4 | OVA prerequisites | `ova-prerequisites_mtv` | NFS share layout, folder scanning |
| 5.5 | OpenShift Virt prerequisites | `cnv-prerequisites_mtv` | Matching MTV versions, OCP Virt 4.16+ |
| 5.5.1 | Live migration prerequisites | `cnv-cnv-live-prerequisites_mtv` | MTV 2.10+, OCP Virt 4.20+, DecentralizedLiveMigration feature gate |
| 5.6 | Software compatibility | `compatibility-guidelines_mtv` | Version matrix: OCP 4.21/4.20/4.19, vSphere 6.5+, RHV 4.4 SP1+, OpenStack 16.1+ |
| 5.6.1 | Operator life cycles | `openshift-operator-life-cycles` | Link to OCP operator lifecycle |
| 6 | Installing / configuring MTV | `assembly_installing-mtv-operator_mtv` | Install and configure the operator |
| 6.1 | Install via web console | `installing-mtv-operator_web` | UI-based install steps |
| 6.2 | Install via CLI | `installing-mtv-operator_cli` | CLI manifests for install |
| 6.3 | Configuring MTV Operator | `configuring-mtv-operator_mtv` | ForkliftController CR settings |
| 6.4 | MTV Operator parameters | `ref_mtv-operator-parameters_mtv` | Full parameter table |
| 6.5 | Max VM inflight | `ref_max-concurrent-vms_mtv` | `controller_max_vm_inflight` tuning |
| 7 | Migrating VMs via web console | `assembly_migrating-vms-web-console_mtv` | MTV UI walkthrough |
| 7.1 | Navigating MTV pages | `navigating-mtv-pages_mtv` | Providers, Migration plans, Mappings, Overview pages |
| 7.2 | The MTV user interface | `mtv-ui_mtv` | UI layout overview |
| 7.2.1 | Tips and tricks panel | `tips-and-tricks-panel_mtv` | Contextual guidance dropdown for providers, migration, troubleshooting |
| 7.3 | MTV Overview page | `mtv-overview-page_mtv` | Overview page tabs |
| 7.3.1 | Overview tab | `overview-tab_mtv` | Charts, health, welcome section |
| 7.3.2 | YAML tab | `overview-yaml-tab_mtv` | ForkliftController CR editor |
| 7.3.3 | Health tab | `overview-health-tab_mtv` | Pod status table and conditions |
| 7.3.4 | History tab | `overview-history-tab_mtv` | Migration history with filters |
| 7.3.5 | Settings tab | `overview-settings-tab_mtv` | Max concurrent VMs, CPU/memory limits, precopy interval, transfer network |
| 7.3.6 | Controller transfer network | `choosing-controller-transfer-network_mtv` | Select a different controller transfer network |
| 7.4 | Preparing VMs for migration | `preparing-vms-for-migration_mtv` | Pre-migration VM configuration tasks |
| 7.4.1 | Renaming VMs | `proc_renaming-vms-for-migration_mtv` | DNS-compliant name adjustments |
| 7.4.2 | Target power state | `proc_configuring-target-power-state-vms_mtv` | off / on / auto per VM |
| 8 | Migrating VMs via CLI | `assembly_migrating-vms-cli_mtv` | CLI-based migration |
| 8.1 | Non-admin permissions | `non-admin-permissions_cli` | RBAC roles for plan components |
| 9 | Network and storage mapping | `assembly_mapping-networks-storage_mtv` | Maps concepts |
| 9.1 | About network maps | `about-network-maps_mtv` | Plan-specific vs ownerless |
| 9.2 | About storage maps | `about-storage-maps_mtv` | Plan-specific vs ownerless |
| 9.3 | Ownerless storage maps | `con_creating-ownerless-storage-maps-ui_mtv` | Creating ownerless maps |
| 10 | VMware migration planning | `assembly_planning-migration-vmware_mtv` | Full VMware planning chapter |
| 10.4 | Storage copy offload | `about-storage-copy-offload_vmware` | XCOPY-based accelerated migration (GA for cold, Tech Preview for warm) |
| 10.4.1 | How SCO works | `how-storage-copy-offload-works_vmware` | Array-level disk cloning |
| 10.4.2 | Supported storage providers | `storage-copy-offload-works-supported-providers_vmware` | Hitachi, NetApp, Pure, Dell, HPE, Infinidat, IBM |
| 10.4.3 | SCO planning steps | `proc_storage-copy-offload-steps_vmware` | Pre-migration checklist |
| 10.4.4 | SCO cloning methods | `con_copy-methods-sco_vmware` | VIB vs SSH methods |
| 10.4.4.1 | SSH advantages | `advantages_of_the_ssh_method` | No VIB install needed |
| 10.4.4.2 | SCO VIB setup | `proc_storage-copy-offload-vib-set-up_vmware` | Install VIB on ESXi |
| 10.4.4.3 | SCO SSH setup | `proc_storage-copy-offload-general-ssh-set-up_vmware` | SSH key configuration |
| 10.4.4.3.2 | SSH security recs | `security_recommendations` | Key rotation, short-lived keys |
| 10.4.4.3.3 | SCO auto SSH keys | `proc_storage-copy-offload-auto-ssh-set-up_vmware` | Auto-generated RSA keys |
| 10.4.4.3.4 | SCO manual SSH keys | `proc_storage-copy-offload-manual-ssh-set-up_vmware` | Manually generated restricted keys |
| 10.4.5 | SCO via UI | `proc_storage-copy-offload-ui_vmware` | UI wizard with copy offload |
| 10.5 | Adding VMware provider | `adding-source-provider_vmware` | vCenter / ESXi source provider |
| 10.6 | VMware migration network | `selecting-migration-network-for-vmware-source-provider_vmware` | NFC network selection |
| 10.7 | Adding OCP Virt dest provider | `adding-source-provider_dest_vmware` | Destination provider for VMware plans |
| 10.8 | OCP Virt migration network | `selecting-migration-network-for-virt-provider_dest_vmware` | Transfer network for destination |
| 10.9 | VMware plan wizard | `creating-plan-wizard-vmware_vmware` | Step-by-step plan creation |
| 10.10 | VMware plan settings | `configuring-vmware-plan-settings_vmware` | Volume/PVC/network name templates, raw copy mode, VM scheduling, affinity |
| 10.11 | LUKS-encrypted disks | `con_migration-of-luks-encrypted-disks_vmware` | Migrating encrypted VMs |
| 10.12 | NBDE with Clevis | `proc_enabling-nbde-with-clevis_vmware` | Network-Bound Disk Encryption |
| 10.13 | Scheduling importer pods | `about-scheduling-importer-pods_vmware` | Schedule destination nodes for virt-v2v importer pods (cold VMware only) |
| 11 | RHV migration planning | `assembly_planning-migration-rhv_mtv` | Full RHV planning chapter |
| 11.4 | Adding RHV provider | `adding-source-provider_rhv` | RHV source provider setup |
| 11.7 | RHV plan wizard | `creating-plan-wizard-rhv_rhv` | RHV migration plan creation |
| 12 | OpenStack migration planning | `assembly_planning-migration-osp_mtv` | Full OpenStack planning chapter |
| 12.4 | Adding OpenStack provider | `adding-source-provider_ostack` | OpenStack source provider setup |
| 12.7 | OpenStack plan wizard | `creating-plan-wizard-ostack_ostack` | OpenStack migration plan creation |
| 13 | OVA migration planning | `assembly_planning-migration-ova_mtv` | Full OVA planning chapter |
| 13.4 | Adding OVA provider | `adding-source-provider_ova` | OVA source provider setup |
| 13.7 | OVA plan wizard | `creating-plan-wizard-ova_ova` | OVA migration plan creation |
| 13.8 | OVA web upload | `proc_configuring-ova-web-upload_ova` | Upload OVA files via browser to NFS share |
| 14 | OCP Virt migration planning | `assembly_planning-migration-cnv_mtv` | Full OCP Virt planning chapter |
| 14.4 | Adding OCP Virt source provider | `adding-source-provider_cnv` | OCP Virt source provider setup |
| 14.7 | OCP Virt plan wizard | `creating-plan-wizard-cnv_cnv` | OCP Virt migration plan creation |
| 14.7.1 | Live migration plan wizard | `creating-plan-wizard-cnv-live_cnv` | Live migration plan creation |

## Migration Guide

**Base URL:** `https://docs.redhat.com/en/documentation/migration_toolkit_for_virtualization/2.11/html-single/migrating_your_virtual_machines_to_red_hat_openshift_virtualization/index`

### Chapter / section anchor reference

| Ch. | Section | Anchor ID | Description |
|-----|---------|-----------|-------------|
| 1 | Performing a migration | `con_performing-migration-intro_mtv` | Overview of running migrations |
| 2 | Migrating from VMware | `assembly_migrating-from-vmware_mtv` | VMware migration via UI and CLI |
| 2.2 | Running VMware plan (UI) | `running-migration-plan_vmware` | Start a VMware migration plan |
| 2.2.1 | Migration plan options | `migration-plan-options-ui_vmware` | Edit, duplicate, archive, delete plans |
| 2.2.2 | Cancel VMware migration (UI) | `canceling-migration-ui_vmware` | Cancel in-progress migration via UI |
| 2.3 | VMware CLI migration | `proc_migrating-vms-cli-vmware_vmware` | Full CLI manifests for VMware |
| 2.4 | Storage copy offload CLI | `proc_storage-copy-offload-cli_vmware` | CLI-based SCO migration |
| 2.4.1 | VMware moRef retrieval | `retrieving-vmware-moref_vmware` | Get Managed Object Reference IDs |
| 2.4.2 | Shared disks | `mtv-shared-disks_vmware` | Multi-writer shared disk handling |
| 2.4.3 | MTV template utility | `mtv-template-utility_vmware` | Go template utility for VM names |
| 3 | Migrating from RHV | `assembly_migrating-from-rhv_mtv` | RHV migration via UI and CLI |
| 3.2 | Running RHV plan (UI) | `running-migration-plan_rhv` | Start an RHV migration plan |
| 3.3 | RHV CLI migration | `proc_migrating-vms-cli-rhv_rhv` | Full CLI manifests for RHV |
| 4 | Migrating from OpenStack | `assembly_migrating-from-osp_mtv` | OpenStack migration via UI and CLI |
| 4.2 | Running OpenStack plan (UI) | `running-migration-plan_ostack` | Start an OpenStack migration plan |
| 4.3 | OpenStack CLI migration | `proc_migrating-vms-cli-ostack_ostack` | Full CLI manifests for OpenStack |
| 5 | Migrating from OVA | `assembly_migrating-from-ova_mtv` | OVA migration via UI and CLI |
| 5.3 | Running OVA plan (UI) | `running-migration-plan_ova` | Start an OVA migration plan |
| 5.4 | OVA CLI migration | `proc_migrating-vms-cli-ova_ova` | Full CLI manifests for OVA |
| 6 | Migrating from OCP Virt | `assembly_migrating-from-virt_mtv` | OCP Virt migration via UI and CLI |
| 6.2 | Running OCP Virt plan (UI) | `running-migration-plan_cnv` | Start an OCP Virt migration plan |
| 6.3 | OCP Virt CLI migration | `proc_migrating-vms-cli-cnv_cnv` | CLI walkthrough for OCP Virt cold migration |
| 6.4 | Live migration CLI | `migrating-live-cnv-cnv-vms-cli_cnv` | CLI walkthrough for live migration |
| 7 | Advanced migration options | `assembly_advanced-migration-options_mtv` | Hooks, validation, UDN, scheduling |
| 7.1 | Warm migration precopy intervals | `changing-precopy-intervals_mtv` | Adjust snapshot intervals |
| 7.2 | Custom validation rules | `con_creating-custom-rules-validation_mtv` | OPA Rego validation rules |
| 7.2.1 | About Rego files | `about-rego-files_mtv` | Rego file structure |
| 7.2.2 | Default validation rules | `accessing-default-validation-rules_mtv` | View built-in rules |
| 7.2.3 | Creating validation rules | `proc_creating-validation-rules_mtv` | Write and apply custom rules |
| 7.2.4 | Inventory rules version | `updating-inventory-rules-version_mtv` | Update validation rules version |
| 7.2.5 | Inventory service JSON | `retrieving-inventory-service-json_mtv` | Retrieve inventory JSON |
| 7.3 | Pre/post-migration hooks | `about-hooks-for-migration-plans_mtv` | Ansible playbook hooks |
| 7.3.1 | Hook workflow | `hook-execution_mtv` | How hooks run during migration |
| 7.3.2 | Add hook via UI | `adding-migration-hook-via-ui_mtv` | UI-based hook configuration |
| 7.3.3 | Add hook via CLI | `adding-migration-hook-via-cli_mtv` | CLI-based hook configuration |
| 7.4 | User-defined networks (UDN) | `about-udn_mtv` | UDN support for migrations |
| 7.5 | Target VM scheduling | `con_scheduling-target-vms-intro_mtv` | Node selector, affinity, labels |
| 7.5.1 | About scheduling target VMs | `target-vm-scheduling-about_mtv` | Scheduling concepts |
| 7.5.2 | Scheduling prerequisites | `target-vm-scheduling-prerequisites_mtv` | Requirements for scheduling |
| 7.5.3 | Scheduling options | `target-vm-scheduling-options_mtv` | Available scheduling features |
| 7.5.4 | Scheduling via CLI | `configuring-target-vm-scheduling-cli_mtv` | CLI-based scheduling config |
| 7.5.5 | Scheduling via UI | `configuring-target-vm-scheduling-ui_mtv` | UI-based scheduling config |
| 8 | Upgrading / uninstalling MTV | `assembly_upgrading-uninstalling-mtv_mtv` | Upgrade and uninstall |
| 8.1 | Upgrade MTV | `upgrading-mtv-ui_mtv` | Upgrade procedure |
| 8.2 | Uninstall via UI | `uninstalling-mtv-ui_mtv` | UI-based uninstall |
| 8.3 | Uninstall via CLI | `uninstalling-mtv-cli_mtv` | CLI-based uninstall |
| 9 | Understanding MTV migration | `assembly_understanding-mtv-migration_mtv` | CRs, services, workflows |
| 9.1 | Custom resources / services | `mtv_custom_resources` | CR reference |
| 9.1.1 | MTV custom resources | `mtv-custom-resources_mtv` | Custom resource list |
| 9.1.2 | MTV services | `mtv_services` | Service reference |
| 9.2 | High-level migration workflow | `mtv-workflow_mtv` | High-level migration pipeline |
| 9.2.1 | Detailed migration workflows | `detailed-migration-workflows_mtv` | Per-provider workflows |
| 9.2.2 | How MTV uses virt-v2v | `virt-v2v-mtv_mtv` | virt-v2v conversion process |
| 9.2.3 | Raw copy mode | `raw-copy-mode_mtv` | Copy without virt-v2v conversion |
| 9.2.4 | Device compatibility mode | `con_device-compatibility-mode-raw-copy-migrations_mtv` | SATA/E1000E compatibility devices |
| 10 | Troubleshooting | `assembly_troubleshooting-migration_mtv` | Debugging failed migrations |
| 10.1 | Troubleshooting workflow | `troubleshooting-workflow_mtv` | Step-by-step troubleshooting guide |
| 10.2 | Common migration issues | `common-migration-issues_mtv` | Frequent problems and solutions |
| 10.3 | Error messages | `error-messages_mtv` | Common error reference |
| 10.3.1 | Warm import retry limit | `resolving-warm-import-retry_mtv` | Resolve warm import retry errors |
| 10.3.2 | Disk resize errors | `resolving-disk-resize_mtv` | Resolve disk resize errors |
| 10.3.3 | OVA connection errors | `resolving-ova-connection_mtv` | Resolve OVA connection test errors |
| 10.3.4 | VDDK image pull errors | `resolving-vddk-image-pull_mtv` | Resolve VDDK image pull errors |
| 10.3.5 | VDDK vSAN errors | `resolving-vddk-vsan_mtv` | Resolve VDDK vSAN errors |
| 10.4 | SCO troubleshooting | `con_troubleshooting-storage-copy-offload_mtv` | Storage copy offload issues |
| 10.4.1 | vSphere-ESXi connectivity | `vsphere-esxi-connectivity_mtv` | ESXi connectivity troubleshooting |
| 10.4.2 | SSH error messages | `ssh-error-messages_mtv` | SSH-related SCO errors |
| 10.4.3 | NetApp errors | `netapp-errors_mtv` | NetApp-specific SCO errors |
| 10.5 | must-gather | `using-must-gather_mtv` | Collect diagnostic data |
| 10.6 | Collected logs / CR info | `collected-logs-cr-info_mtv` | What must-gather collects |
| 10.6.1 | Logs via UI | `accessing-logs-ui_mtv` | UI log access |
| 10.6.2 | Logs via CLI | `accessing-logs-cli_mtv` | CLI log access |
| 11 | Performance recommendations | `assembly_mtv-performance-recommendations_mtv` | Optimize migration speed |
| 11.1 | Fast storage/network | `ref_fast-storage-network-speeds_mtv` | Storage and network speed guidance |
| 11.2 | Fast datastore reads | `ref_fast-datastore-read-speeds_mtv` | Datastore read optimization |
| 11.3 | Endpoint types | `ref_endpoint-types_mtv` | vCenter vs ESXi endpoints |
| 11.4 | ESXi performance | `mtv-esxi-performance_mtv` | ESXi-specific tuning |
| 11.4.1 | Single ESXi host | `mtv-single-esxi-host-performance_mtv` | Single-host limits |
| 11.4.2 | Multiple ESXi hosts | `mtv-multiple-esxi-host-performance_mtv` | Multi-host scaling |
| 11.5 | Migration network performance | `mtv-different-migration-network-performances_mtv` | Network comparison |
| 11.6 | Avoid network load | `ref_avoid-network-load_mtv` | Migration network best practices |
| 11.7 | Concurrent disk migrations | `ref_control-concurrent-disk-migrations_mtv` | Parallel disk tuning |
| 11.8 | Concurrent migrations | `ref_concurrent-migrations-faster-migrations_mtv` | Parallel VM tuning |
| 11.9 | Multiple hosts | `ref_multiple-hosts-faster-migrations_mtv` | Multi-host performance |
| 11.10 | Plan sizing | `ref_multiple-migration-plans-vs-single_mtv` | One large vs many small plans |
| 11.11 | Max cold migration values | `ref_maximum-values-cold-migrations_mtv` | Cold migration throughput |
| 11.12 | Warm migration recs | `ref_warm-migration-recommendations_mtv` | Warm-specific tuning |
| 11.13 | Max warm migration values | `ref_maximum-values-warm-migrations_mtv` | Warm migration throughput |
| 11.14 | Large disks | `ref_migrating-vms-large-disks_mtv` | Large disk migration guidance |
| 11.15 | AIO/NBD buffer tuning | `mtv-aio-buffer_mtv` | AIO buffer overview |
| 11.15.3 | Enable AIO buffer | `mtv-enable-aio-buffer_mtv` | Enable AIO buffer |
| 11.15.4 | Disable AIO buffer | `mtv-disable-aio-buffer_mtv` | Disable AIO buffer |
| 11.16 | Performance addendum | `mtv-performance-addendum_mtv` | Additional performance data |
| 12 | Telemetry | `mtv-telemetry_mtv` | MTV telemetry data collection |

## Quick Topic Finder

Use this section to match user questions to the right deep link.
Format: `<Base URL>#<anchor_id>`

- **"How do I install MTV?"** → Planning `#assembly_installing-mtv-operator_mtv`
- **"What are the VMware prerequisites?"** → Planning `#vmware-prerequisites_mtv`
- **"How do I set up VDDK?"** → Planning `#creating-vddk-image_mtv`
- **"Cold vs warm migration?"** → Planning `#assembly_cold-warm-migration_mtv`
- **"How do I choose migration type?"** → Planning `#choosing-migration-type_mtv`
- **"What is live migration?"** → Planning `#assembly_live-migration_mtv`
- **"How do I create a migration plan?"** → Planning `#navigating-mtv-pages_mtv` (UI) or `#assembly_migrating-vms-cli_mtv` (CLI)
- **"How do I map networks/storage?"** → Planning `#assembly_mapping-networks-storage_mtv`
- **"How do I run a VMware migration?"** → Migration `#running-migration-plan_vmware`
- **"How do I migrate from RHV?"** → Migration `#assembly_migrating-from-rhv_mtv`
- **"How do I migrate from OpenStack?"** → Migration `#assembly_migrating-from-osp_mtv`
- **"How do I migrate OVA files?"** → Migration `#assembly_migrating-from-ova_mtv`
- **"How do I upload OVA files?"** → Planning `#proc_configuring-ova-web-upload_ova`
- **"How do I use hooks?"** → Migration `#about-hooks-for-migration-plans_mtv`
- **"How do I add custom validation rules?"** → Migration `#con_creating-custom-rules-validation_mtv`
- **"Migration is failing / troubleshooting"** → Migration `#assembly_troubleshooting-migration_mtv`
- **"Common migration issues?"** → Migration `#common-migration-issues_mtv`
- **"How do I improve migration speed?"** → Migration `#assembly_mtv-performance-recommendations_mtv`
- **"How do I use storage copy offload?"** → Planning `#about-storage-copy-offload_vmware` or Migration `#proc_storage-copy-offload-cli_vmware`
- **"How do I schedule target VMs?"** → Migration `#con_scheduling-target-vms-intro_mtv`
- **"How do I schedule importer pods?"** → Planning `#about-scheduling-importer-pods_vmware`
- **"LUKS / encrypted disks?"** → Planning `#con_migration-of-luks-encrypted-disks_vmware`
- **"NBDE / Clevis?"** → Planning `#proc_enabling-nbde-with-clevis_vmware`
- **"How do I uninstall MTV?"** → Migration `#uninstalling-mtv-ui_mtv` (UI) or `#uninstalling-mtv-cli_mtv` (CLI)
- **"What is must-gather?"** → Migration `#using-must-gather_mtv`
- **"User-defined networks / UDN?"** → Migration `#about-udn_mtv`
- **"Raw copy mode?"** → Migration `#raw-copy-mode_mtv`
- **"virt-v2v?"** → Migration `#virt-v2v-mtv_mtv`
- **"Non-admin permissions?"** → Planning `#non-admin-permissions_cli`
- **"Operator parameters?"** → Planning `#ref_mtv-operator-parameters_mtv`
- **"Max concurrent VMs?"** → Planning `#ref_max-concurrent-vms_mtv`
- **"VMware privileges?"** → Planning `#vmware-privileges_mtv`
- **"Network ports?"** → Planning `#ports_mtv`
- **"Software compatibility?"** → Planning `#compatibility-guidelines_mtv`
- **"VMware plan settings / templates?"** → Planning `#configuring-vmware-plan-settings_vmware`
- **"Tips and tricks?"** → Planning `#tips-and-tricks-panel_mtv`
- **"MTV settings?"** → Planning `#overview-settings-tab_mtv`
- **"Transfer network?"** → Planning `#choosing-controller-transfer-network_mtv`
- **"Understanding MTV migration?"** → Migration `#assembly_understanding-mtv-migration_mtv`
- **"MTV custom resources?"** → Migration `#mtv_custom_resources`
- **"Device compatibility mode?"** → Migration `#con_device-compatibility-mode-raw-copy-migrations_mtv`
