# README

This is an example of how to build a composabl suitable container yourself for full control.

### Build the Sim

To build the sim wrapper, run the following command:

```bash
docker build -t composabl/sim-demo .
```

### Run the Sim

```bash
docker run --rm -it -p 1337:1337 composabl/sim-demo
```
