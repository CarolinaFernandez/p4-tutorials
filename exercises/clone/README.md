# Implementing Packet Cloning

## Introduction

The objective of this exercise is to write a P4 program that
implements packet cloning in IPv4.

Cloning a packet can be done in two ways: (i) from ingress-to-egress
and (ii) from egress-to-egress. The source and destination points
determine where the cloning action takes place (ingress or egress) and
in which pipeline the packet is cloned to (egress).

To clone the packet, the switch must perform the following actions for
every packet: (i) determine the type of the clone and relate the
packet to a mirror session ID, so it can be later identified, (ii) 
determine if the packet instance type corresponds to that of a cloned
packet so that some actions can be applied to modify its headers (it
will be easier to quickly determine what the copy is).
 
Your switch will have a single table, which the control plane will
populate with static rules. Each rule will map an IP address to the
MAC address and output port for the next hop. Besides, commands are
provided to the switches to enforce a specific port to which cloned
packets will be forwarded. We have already defined the control plane
rules, so you only need to implement the data plane logic of your P4
program.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the
> reference.

## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`clone.p4`, which initially forwards one IPv4 packet. Your job will
be to extend this skeleton program to properly clone packets.

Before that, let's compile the incomplete `clone.p4` and bring
up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   make run
   ```
   This will:
   * compile `clone.p4`, and
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
4. In `h1`'s xterm, send a message to `h2`:
   ```bash
   ./send.py 10.0.2.2 "P4 is cool"
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

The message was received because the forwarading behaviour is
provided. However, a copy is expected in the exercise.
Your job is to extend this file so it initially clones the
packet to be forwarded.

### A note about the control plane

A P4 program defines a packet-processing pipeline, but the rules
within each table are inserted by the control plane. When a rule
matches a packet, its action is invoked with parameters supplied by
the control plane as part of the rule.

In this exercise, we have already implemented the the control plane
logic for you. As part of bringing up the Mininet instance, the
`make run` command will install specific mirroring/cloning commands and
packet-processing rules in the tables of each switch. These are defined
in the `sX-commands.txt` and the `sX-runtime.json` files, where `X`
corresponds to the switch number.

**Important:** We use P4Runtime to install the control plane rules. The
content of files `sX-commands.txt` and `sX-runtime.json` refer to specific
commands, names of tables, keys, and actions, as defined in the P4Info file
produced by the compiler (look for the file `build/clone.p4info` after
executing `make run` or `compile.sh`). Any changes in the P4 program that
add or rename tables, keys, or actions will need to be reflected in
the `sX-runtime.json` files.

## Step 2: Implement packet cloning

The `clone.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments. Your implementation should follow
the structure given in this file---replace each `TODO` with logic
implementing the missing piece.

A complete `clone.p4` will contain the following components:

1. Header type definitions for Ethernet (`ethernet_t`) and IPv4 (`ipv4_t`).
2. Parsers for Ethernet and IPv4 that populate `ethernet_t` and `ipv4_t` fields.
3. An action to drop a packet, using `mark_to_drop()`.
4. An action (called `ipv4_forward`) that:
	1. Sets the egress port for the next hop. 
	2. Updates the ethernet destination address with the address of the next hop. 
	3. Updates the ethernet source address with the address of the switch. 
	4. Decrements the TTL.
5. A control ingress that:
    1. Defines a table that will read an IPv4 destination address, and
       invoke either `drop` or `ipv4_forward`.
    2. **TODO**: Defines the clone type and the mirror session ID.
    3. An `apply` block that applies the table and call the clone action.
6. A control egress that:
    1. Implements a way to clear the TTL value and to change the source IPv4 address.
    2. **TODO** An `apply` block that determines whether the packet is cloned, and if
       so, call the relevant actions. 
7. A deparser that selects the order
    in which fields inserted into the outgoing packet.
8. A `package` instantiation supplied with the parser, control, and deparser.
    > In general, a package also requires instances of checksum verification
    > and recomputation controls. These are not necessary for this tutorial
    > and are replaced with instantiations of empty controls.

## Step 3: Run your solution

Follow the instructions from Step 1. This time, your message from `h1`
should be delivered twice to `h2`, with some minor differences in its headers.

### Food for thought

Questions to consider:
 - Is the order between forwarding and cloning relevant? How does it react
   for each case?
 - Why is a cloned packet being forwarded to the source of the communication?
   (That is, when sending from h1 to h2, why the packet is also reaching h1?)
 - Why is a default egress port assigned per switch in the `sX-commands.txt`,
   instead of leveraging on `standard_metadata.egress_spec`?

### Troubleshooting

There are several problems that might manifest as you develop your program:

1. `clone.p4` might fail to compile. In this case, `make run` will
report the error emitted from the compiler and halt.

2. `clone.p4` might compile, and the control plane rules might be
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

## Next Steps

Congratulations, your implementation works! Move on to
[Basic](../basic).
