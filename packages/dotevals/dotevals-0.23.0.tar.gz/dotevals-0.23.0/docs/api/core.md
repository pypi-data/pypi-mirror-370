# Core Module

The core module contains the fundamental components of dotevals, including the `@foreach` decorator and essential evaluation functions.

## @foreach Decorator

The main decorator that transforms functions into evaluations. This is the primary entry point for most users.

**Usage**: `@foreach("param1,param2", dataset)`

::: dotevals.foreach

## ForEach Class

The configurable version of the foreach decorator that allows custom retry strategies, concurrency, and storage backends.

::: dotevals.ForEach

## Core Functions

Essential functions for advanced usage and programmatic access.

::: dotevals.core
