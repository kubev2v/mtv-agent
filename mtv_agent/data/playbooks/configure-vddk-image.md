---
name: configure-vddk-image
category: Setup
description: >
  Check, set, update, or remove the VDDK image setting required
  for vSphere migrations.
tools:
  - mtv_read (server: kubectl-mtv)
  - mtv_write (server: kubectl-mtv)
---

# Configure VDDK Image

Goal: view the current VDDK init-image setting and let the user set, update, or remove it.

The VDDK (Virtual Disk Development Kit) image is required for vSphere disk transfers.
Without it, vSphere migrations will fail.

## Inputs

Collect before starting:
- **namespace** -- check session context first; **ASK the user** only if missing.

Do NOT ask for the VDDK image URL upfront -- step 1 determines whether it is needed.

## Steps

### Step 1 -- Check current VDDK image

```json
mtv_read { "command": "settings get", "flags": { "setting": "vddk_image", "namespace": "<NAMESPACE>", "output": "markdown" } }
```

Report the current value to the user.

**IF a VDDK image is already configured**: **ASK the user** what they want to do:
- Keep it (no changes)
- Update it (user must provide the new image URL)
- Remove it

**IF not set**: **ASK the user** if they want to set one. If yes, they must provide
the image URL (e.g., `quay.io/kubev2v/vddk:latest`). Do NOT guess the image URL.

**IF the user only wanted to check the current value**: stop here and report it.

### Step 2 -- Apply the change

**IF the user wants to set or update** (user provides `<VDDK_IMAGE>`):

```json
mtv_write { "command": "settings set", "flags": { "setting": "vddk_image", "value": "<VDDK_IMAGE>", "namespace": "<NAMESPACE>" } }
```

**IF PASS** (return_value=0): continue to step 3.
**IF FAIL**: report the error. Common causes:
- **Permission denied / forbidden**: user may not have admin access.
  Suggest contacting a cluster admin.
- **Invalid value**: check the image URL format (should be a container image reference).

**IF the user wants to remove**:

```json
mtv_write { "command": "settings unset", "flags": { "setting": "vddk_image", "namespace": "<NAMESPACE>" } }
```

**IF PASS**: continue to step 3.
**IF FAIL**: report the error to the user.

### Step 3 -- Verify

```json
mtv_read { "command": "settings get", "flags": { "setting": "vddk_image", "namespace": "<NAMESPACE>", "output": "markdown" } }
```

Confirm the setting reflects the expected value.

**IF the verified value matches what was intended**: continue to step 4.
**IF the verified value does not match**: warn the user the setting may not have taken effect.
Suggest retrying or checking permissions.

### Step 4 -- Report

**IF the image was set or updated**:
> VDDK image is now configured as "<VDDK_IMAGE>". vSphere migrations will use this
> image for disk transfers.

**IF the image was removed**:
> VDDK image setting has been removed. The controller will use its default value.

**IF no changes were made**:
> VDDK image remains set to "<CURRENT_VALUE>". No changes were made.
