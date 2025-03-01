# MISSION

Empowering SideFX Houdini Artists with fast growing AI technologies to create better and faster Houdini projects.

# HOUDINI 2 CHAT

Imagine Houdini Artists have a tool that enables them to instantly chat with any AI program about their Complex Houdini Scenes without describing them, and for free.

Our first project, Houdini 2 Chat is an HDA (Houdini Digital Asset) that brings Houdini scenes to any AI chat and any AI Code assistants.

**Watch the video to see it in action**

<div align="center" style="max-width: 300px; margin: 0 auto;">
  
[![Video Title](docs/images/youtube_cover_link.png)](https://www.youtube.com/watch?v=zzEDeaTQBZI)

</div>

>[!WARNING]
> The project is in **early development stage `(Proof of concept)`**. It is experimental and missing some features.

# Use Cases

- Explain complex Houdini scenes
- Accelerate learning of Houdini
- Get help with coding in VEX, Python, or HScript
- Get suggestions to fix problems in Houdini scenes
- Find better workflows from thousands of Houdini Nodes and Parameters you may not know.

## How to Install
- Download the latest [release](https://github.com/rendermagix/houdini2chat/releases) from the Github [Repo]()
- To install globally, add it in Houdini otls Folder ([Where?](https://www.sidefx.com/docs/houdini/assets/install.html)).

## How to Use
- Open any Houdini Scene, browse to your network
- Drop a Houdini 2 Chat Node
- Hit Export 2 Chat Button.


Now you can chat with the generated file(s) using any AI chat or AI code assistant.

## Compatible AI Tools
### Tested with
- ChatGPT Plus (regular and Canvas mode) (should work with the free version too)
- Claude Sonnet 3.7 (regular and Artifacts mode)
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

0.1.0 &nbsp; [First Release](https://github.com/rendermagix/houdini2chat/releases/tag/v0.1.0)

# Next Steps
- Gather initial feedback on the Houdini 2 Chat concept.
- Stabilize the Houdini 2 Chat HDA while in feedback mode.
- Decide what's next.

# Big Future Ideas
- Create a benchmark - Houdini Benchmark - that evaluates the performance of the tools in different LLMs (Large Language Models)
- Create a Houdini tuned LLM Model.
- Make a better integration inside SideFX Houdini.
- Implement innovative ways to update Houdini scenes using Generative AI.
  
# FAQ
<details>
<summary>Click to Expand Questions/Answers</summary>
<br>

**Q: How can I make Houdini2Chat HDA visible to all files?**  
A: (Windows) simply put the hda in documents/houdini20.5/otls<br>Alternatively, add the path to Houdini2Chat HDA in $HOUDINI_PATH<br> **Make sure to restart Houdini!**
<br>


  
</details>
