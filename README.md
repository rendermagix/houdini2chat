# MISSION

Empowering SideFX Houdini Artists with the fast growing AI technologies to create better and faster Houdini projects.

# HOUDINI 2 CHAT

Our first project, Houdini 2 Chat is an HDA (Houdini Digital Asset) that transforms all or parts of a Houdini scene into a format that is efficient for use with AI chat and AI Code assistants.

## Current Status
- The project is in the early stages of development (Proof of concept).
- It is experimental and missing many features.


# Table of Contents

- [MISSION](#mission)
- [HOUDINI 2 CHAT](#houdini-2-chat)
  - [Current Status](#current-status)
- [Table of Contents](#table-of-contents)
- [Use Cases](#use-cases)
  - [How it works](#how-it-works)
  - [Compatible AI Tools](#compatible-ai-tools)
    - [Tested with](#tested-with)
    - [Should also work with (Not Tested)](#should-also-work-with-not-tested)
- [Compatible Houdini Versions](#compatible-houdini-versions)
- [Features List](#features-list)
  - [In the development pipeline](#in-the-development-pipeline)
- [Releases](#releases)
- [Next Steps](#next-steps)
- [Big Future Ideas](#big-future-ideas)


# Use Cases

- Explain complex Houdini scenes
- Accelerate learning of Houdini
- Get help with coding in VEX, Python, or HScript
- Get suggestions to fix problems in Houdini scenes
- Find better workflows from thousands of Houdini Nodes and Parameters you may not know.

## How it works
- Download the HDA and Install it in Houdini.
- Drop the HDA inside any object node in Houdini.
- Configure if needed and Hit the "Export" button.

Now you can chat with the generated file(s) using any AI chat or AI code assistant.

## Compatible AI Tools
### Tested with
- ChatGPT Plus in canvas mode (should work with the free version too)
- Github Copilot (Pro) Chat in VS Code (should work with the free version too)

### Should also work with (Not Tested)
- JetBrains IDE/Github Copilot
- Visual Studio/Github Copilot
- Xcode/Github Copilot
- Cursor

# Compatible Houdini Versions
- Houdini 20.5 - Not tested in earlier versions.
- Windows 10/11 - not tested on Linux/MacOS.
- License: Tested on Apprentice/Indie Licenses.

# Features List
- Export Houdini Networks on any Obj Node.
- Export Multiple Nodes.
- Exports Network Boxes.
- Export Node Parameters/Values/References/Expressions.
- Export One File per Node, One File per Network Box.
- Define Filename format.
- Filter Specific Network Boxes.

## In the development pipeline
- Recursive Loops, Recursive Networks.
- subnetworks and hda contents.
- Better handling of nodes order.
- Better handling of multiple output nodes.
- Better handling of network branches presentation.
- Better handling of Sticky Notes presentation.
- Network errors/warnings.
- Linking to node documentation.
- Linking to node data (points/verts/prim/detail attribs and data)
- Non Obj nodes support.
- Custom representation of popular nodes (Vex Wrangle is already implemented as a function)

# Releases

0.0.1

# Next Steps
- Gather initial feedback on the Houdini 2 Chat concept.
- Stabilize the Houdini 2 Chat HDA while in feedback mode.
- Decide what's next.

# Big Future Ideas
- Create a benchmark - Houdini Benchmark - that evaluates the performance of the tools in different LLMs (Large Language Models)
- Create a Houdini tuned LLM Model.
- Make a better integration inside SideFX Houdini.
- Implement innovative ways to update Houdini scenes using Generative AI.
