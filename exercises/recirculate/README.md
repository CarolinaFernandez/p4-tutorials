# Implementing Packet Recirculation

## Introduction

The objective of this exercise is to write a P4 program that
implements packet recirculation in IPv4.

When a packet is recirculated, it is sent again to both ingress and
egress pipelines once it has gone through previously. This enables applying
a table or action multiple times on a packet.

To recirculate the packet, the switch must perform the following actions for
every packet: (i) determine whether it is (or not) a recirculated packet, (ii)
execute the recirculate method depending on the status defined before.
In this example, the packets carry a custom header which includes, among
others, fields to keep track of how many times the packet goes through a
switch ingress and egress pipeline.

Your switch will have two tables (one to allow typical IPv4 forwarding, another
one to allow forwarding for this custom format, CustomData). The control plane
will populate both with static rules. Therefore, each rule will map an IP
address to the MAC address and output port for the next hop (for IPv4 forwarding)
and will also map a ContentID tag to the output for the next hop (for CustomData
forwarding). The control plane rules are already defined, so you only need to
implement the data plane logic of the P4 program.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the
> reference.

## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`recirculate.p4`, which initially forwards one IPv4 packet. Your job will
be to extend this skeleton program to properly recirculate packets.

Before that, let's compile the incomplete `recirculate.p4` and bring
up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   make run
   ```
   This will:
   * compile `recirculate.p4`, and
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`)
     configured in a triangle, each connected to one host (`h1`, `h2`,
     and `h3`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.2.2`, and `10.0.3.3`.

2. You should now see a Mininet command prompt. Open two terminals
for `h1` and `h2`, respectively:
   ```bash
   mininet> xterm h1 h2
   ```
3. Each host includes a small Python-based messaging client and
server. In `h2`'s xterm, start the server:
   ```bash
   ./receive.py
   ```
4. In `h1`'s xterm, send a message to `h2` in two different ways:
   ```bash
   ./send.py 10.0.2.2 "P4 is cool"
   ./send.py 10.0.2.2 "P4 is cool" --custom_id 102
   ```
   The message will be received once.
5. Type `exit` to leave each xterm and the Mininet command line.
   Then, to stop mininet:
   ```bash
   make stop
   ```
   And to delete all pcaps, build files, and logs:
   ```bash
   make clean
   ```

In the first attempt to send a message, it is properly delivered because
the forwarding behaviour is provided. However, the second is not. This is
because the forwarding (and manipulation) of the CustomData packets are
not provided by default.

### A note about the control plane

A P4 program defines a packet-processing pipeline, but the rules
within each table are inserted by the control plane. When a rule
matches a packet, its action is invoked with parameters supplied by
the control plane as part of the rule.

In this exercise, we have already implemented the the control plane
logic for you. As part of bringing up the Mininet instance, the
`make run` command will install specific mirroring/cloning commands and
packet-processing rules in the tables of each switch. These are defined
in the `sX-runtime.json` files, where `X` corresponds to the switch number.

**Important:** We use P4Runtime to install the control plane rules. The
content of the `sX-runtime.json` files refer to specific names of tables, keys
and actions, as defined in the P4Info file produced by the compiler (look for
the file `build/recirculate.p4info` after executing `make run` or `compile.sh`).
Any changes in the P4 program that add or rename tables, keys, or actions will
need to be reflected in the `sX-runtime.json` files.

## Step 2: Implement packet recirculation

The `recirculate.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments. Your implementation should follow
the structure given in this file---replace each `TODO` with logic
implementing the missing piece.

A complete `recirculate.p4` will contain the following components:

1. Header type definitions for Ethernet (`ethernet_t`), IPv4 (`ipv4_t`) and
   CustomData (`customdata_t`).
    1. **TODO** The `customdata_t` header contains fields to define the times
       the packet traverses the ingress and egress pipelines.
    2. **TODO** Instantiate the `resubmit_meta_t` metadata struct, which shall
       be later used for recirculation.
2. Parsers for Ethernet, IPv4 and CustomData that populate the `ethernet_t`,
   `ipv4_t` and `customdata_t` fields.
3. An action to drop a packet, using `mark_to_drop()`.
4. An action (called `update_customdata_processing_count_by_num`) that:
    1. **TODO** Updates the specific field of CustomData header that counts the number
5. An action (called `ipv4_forward`) that:
    1. Sets the egress port for the next hop. 
    2. Updates the ethernet destination address with the address of the next hop. 
    3. Updates the ethernet source address with the address of the switch. 
    4. Decrements the TTL.
       of times the packet goes through the ingress pipeline. This is achieved
       by setting to a specific number, increment given a number in the
       argument, etc.
6. An action (called `customdata_forward`) that:
    1. **TODO** Sets the egress port for the next hop. 
7. An action (called `recirculate_packet`) that:
    1. **TODO** Sends the packet for recirculation, providing as parameter the
       instantiated metadata from before. 
8. A control ingress that:
    1. Defines a table that will read an IPv4 destination address, and
       invoke either `drop` or `ipv4_forward`.
    2. Defines a table that will read a CustomData custom ID, and
       invoke either `drop` or `customdata_forward`.
    3. **TODO** An `apply` block that updates the counter for the number of times the
       packet with CustomData header traverses the ingress pipeline, then recirculates
       such packet if it is the first time the packet went through the ingress pipeline
       and finally forwards. The forwarding of IPv4 is provided and must be done when
       no packet with the CustomData header is processed.
9. A control egress that:
    1. **TODO** In the `update_customdata_processing_count_by_num` action, updates the
       specific field of CustomData header that counts the number of times the packet goes
       through the egress pipeline. This is achieved by setting to a specific number,
       increment given a number in the argument, etc.
    2. **TODO** An `apply` block that calls the action above.
8. A deparser that selects the order in which fields inserted into the outgoing packet.
9. A `package` instantiation supplied with the parser, control, and deparser.
    > In general, a package also requires instances of checksum verification
    > and recomputation controls. These are not necessary for this tutorial
    > and are replaced with instantiations of empty controls.

## Step 3: Run your solution

Follow the instructions from Step 1. This time, your message (with the CustomData
header) coming from `h1` should be delivered to `h2`. The information updated during the
ingress and egress pipelines can be noticed in the packet that arrived at the destination.

### Food for thought

Questions to consider:
 - Check the number of times the packet goes through the different pipelines.
   Why does it traverse that specific number of times?
   What would happen if recirculate() is commented?
   What would happen if routes are modified so that the packet is delivered
   via an alternate route that includes more network devices?
 - The method that updates the CustomData header fields (which includes the
   number of times the packet traverses a specific pipeline) is increasing
   the current value by a number.
   Why is this working?
   What is the default value for the header field?
 - Check the `receive.py` file.
   Why are there two different types of fields in the definition of
   the CustomData header?
   What is the relationship with the specific fields of the header, as
   provided in the P4 program?

### Troubleshooting

There are several problems that might manifest as you develop your program:

1. `recirculate.p4` might fail to compile. In this case, `make run` will
report the error emitted from the compiler and halt.

2. `recirculate.p4` might compile, and the control plane rules might be
installed, but the switch might not process packets in the desired
way. The `/tmp/p4s.<switch-name>.log` files contain detailed logs
that describing how each switch processes each packet. The output is
detailed and can help pinpoint logic errors in your implementation.

#### Cleaning up Mininet

In the latter two cases above, `make run` may leave a Mininet instance
running in the background. Use the following command to clean up
these instances:

```bash
make stop
```
