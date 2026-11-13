# greengrass-fleet-demo

A tiny, end-to-end example of managing an **edge device fleet** with [AWS IoT
Greengrass](https://docs.aws.amazon.com/greengrass/v2/developerguide/) — from a
device registering itself on first boot, to shipping a component to the whole
fleet, to watching its health come back.

You can SSH into one device to update it. Try doing that on a thousand. This repo
shows the control plane that makes it unnecessary.

![fleet lifecycle](greengrass-fleet.gif)

> This is a **generic, educational** demo. The code recreates the *pattern* from
> scratch — adapt the serial scheme, fleet groups, bucket and policies to your own
> setup.

---

## The two problems (and why they're separate)

The thing that clicks once you build this: **provisioning and deployment are two
different problems.** One is about *identity*, the other about *software*. Keep
them decoupled and the whole thing scales.

| | Provisioning | Deployment |
|---|---|---|
| Goal | register a device | update software |
| Happens | once per device, on first boot | continuously |
| Trigger | device boots with a claim cert | a developer pushes code |
| Result | a Thing + a permanent certificate | new component running on the fleet |

---

## 1. Provisioning — zero-touch

Every device is flashed with the **same image**, carrying only a shared *claim
certificate*: a disposable entry ticket that can do nothing but ask for a real
identity. On first boot the device sends its serial, and a **pre-provisioning
hook** ([`handler.py`](provisioning/pre-provisioning-hook/handler.py)) decides
whether it's allowed in. If it checks out, AWS creates the Thing, issues a
**permanent certificate**, and drops it into a thing group. The claim cert is
then deleted.

One image → many devices, each with its own identity, no manual steps.

```bash
cd provisioning/pre-provisioning-hook
python test_handler.py   # the gatekeeper logic, unit-tested
```

- [`handler.py`](provisioning/pre-provisioning-hook/handler.py) — the validation hook
- [`fleet-provisioning-template.json`](provisioning/fleet-provisioning-template.json) — what AWS creates when a device is allowed in

**Why the claim/permanent split matters:** a leaked claim certificate on its own
is useless — the hook still has to say yes. And a compromised permanent cert only
affects *that one* device, not the fleet.

---

## 2. Deployment — continuous

A push kicks off CI/CD: build, package, upload an **immutable** artifact version
to S3, then register the component version and create a deployment targeting a
**thing group**. Greengrass pushes it over MQTT and every device in the group
installs it — in minutes, no reboot.

```bash
export BUCKET=your-bucket ACCOUNT_ID=123456789012 THING_GROUP=fleet-a

./scripts/1-publish-component.sh   # upload artifact + register component version
./scripts/2-deploy-to-fleet.sh     # deploy that version to the whole group
```

- [`com.example.hello-fleet`](components/com.example.hello-fleet) — a minimal long-running component
- [`recipe.yaml`](components/com.example.hello-fleet/recipe.yaml) — how each device installs and runs it

> Components are **immutable**: you never edit `1.0.0`, you publish `1.0.1`.
> Publishing a component does **not** install it — you always need a deployment too.

---

## 3. Observability — closing the loop

Deploying blind isn't enough. Devices report metrics and logs back to CloudWatch,
alarms fire on the ones that matter, and notifications / tickets get raised. So
it's not "deploy and hope" — you actually see the fleet's health come back. That
return path is the orange arrow in the diagram above.

---

## Layout

```
provisioning/
  pre-provisioning-hook/   the gatekeeper Lambda (+ tests)
  fleet-provisioning-template.json
components/
  com.example.hello-fleet/ example component (recipe + artifact)
scripts/
  1-publish-component.sh   upload + register a component version
  2-deploy-to-fleet.sh     deploy it to a thing group
```

## Notes

- Requires the AWS CLI configured, and a Greengrass core device (or the
  [Greengrass Docker image](https://docs.aws.amazon.com/greengrass/v2/developerguide/run-greengrass-docker.html))
  to actually receive deployments.
- Region defaults to `eu-west-1`; override with `REGION=...`.
