# Knowledgebase Schema

Status: Draft

## Purpose

Define the durable structure of a repository's knowledge base.

## Questions To Settle

- What are the canonical record types?
- Which files are source of truth: structured records, wiki pages, or both?
- How are stable IDs assigned?
- How are aliases represented?
- How are relationships represented?
- Which derived indexes are allowed?

## Initial Direction

The repository will likely separate:

- canonical machine-friendly records
- readable wiki pages
- derived indexes or caches

A consuming project should define those layers precisely before treating this
starter as an accepted specification.
