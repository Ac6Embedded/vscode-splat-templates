# Splat Board Templates

## What is Splat?

Splat, developed by AC6, is an innovative hardware simulation tool based on Renode. Integrated directly into Visual Studio Code.

With Splat, you can accelerate the development, testing, debugging, and simulation of your IoT software without having to modify existing code. This makes the process not only faster but also more economical and reliable, perfect for optimizing your IoT projects.

## What are the board templates ?

The templates are the base files structure that are used to describe a board for simulation and visualization under Splat.

The template consist on a root folder and several files:

```
MY_BOARD
  ├── assets
  │   ├── MY_BOARD.css
  │   └── MY_BOARD.png
  ├── binaries
  ├── platform
  │   ├── MY_BOARD.repl
  │   └── MY_BOARD.svd
  ├── scripts
  │   ├── MY_BOARD.py
  │   └── MY_BOARD.resc
  └── MY_BOARD.html
```  


