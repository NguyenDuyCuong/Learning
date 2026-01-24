# Project Brief: P2P Todo

## Project Name
P2P Todo - Decentralized Task Manager

## Purpose
A decentralized task management application that allows users to manage todos without a central server. It synchronizes data across peers on a local network (LAN) and over the internet (WAN) using a peer-to-peer (P2P) architecture.

## Core Requirements
- Decentralized architecture (no central server).
- Auto-discovery of peers on LAN via mDNS.
- Internet connectivity via DHT and Relays.
- Reliable data synchronization using CRDTs (Conflict-free Replicated Data Types).
- Local persistence of tasks and peer identity.

## Main Goals
- Enable seamless task sharing and updates between devices.
- Ensure data consistency across all connected nodes.
- Provide a simple CLI for task management.
- Support offline-first usage with automatic synchronization when reconnected.

## Project Scope
- CLI-based task management (Add, List, Done, Delete).
- P2P networking layer using `libp2p`.
- CRDT-based data store.
- Basic user identity via persistent Peer IDs.
