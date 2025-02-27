# Imagine

Imagine providing Houdini Artists with a tool that allows them to chat with any AI program about their Complex Houdini Scenes without describing them, for free.  

You could have a network of 100 interconnected nodes, 20 branches, 10 sticky notes, 5 network boxes, 7 loops, and in less than a second, you could chat about it with chatGPT, Claude, Grok, Gemini, Github Copilot, Deepseek, or any future AI tool you can imagine. You could ask them to explain that network for you, document it, visualize it, fix a specific VEX Wrangle or even suggest a better workflow.

<br>

# Problem

`SideFx Houdini` is arguably the most `powerful` 3D software, yet it is also the `most complex` with a huge set of features, procedural nature, network structure, coding ability,  `thousands of node types`.\
Building, understanding, maintaining and debugging Networks for serious tasks can be `overwhelming` and `challenging`.

`AI Productivity tools` have been helping every Product and some of them have been tightly integrated into some of these products, pushing their productivity to the next level.

While most of the 3D software apps are not taking the full advantage of AI tools, `SideFX Houdini` has `unique characteristics` that make it a `perfect candidate` for AI tools integration. The `procedural nature` of Houdini and the fact that its Network description is similar to writing software, `makes it ideal` for AI Tools that understand code, `AI Code Assistants` to be specific.

# Early Approaches

People have tried 2 approaches to use AI tools with Houdini.

## Approach 1 - Chat with LLM

Describe a local problem in a chat with an AI tool and get a solution, like asking AI to write VEX code to do a certain task, or copy/paste VEX code/errors and ask for enhancements/corrections.

**Limitations**
- Too much time wasted `describing complex Networks`, and it's always hard to describe the context.
- Jumping between `multiple chat contexts` back and forth, you have to re-describe it all again.
- When you make `changes to your network`, you may need to describe the whole thing again.

## Approach 2 - LLM API inside Houdini

Use LLM APIs inside Houdini to ask questions and get VEX Code directly inside Houdini. There is a free Houdini HDA that does that.

**Limitations**

- It `doesn't see the context`, only your prompt.
- You are limited to `specific LLMs`
- You `pay` for every API call, `no free option`
- When `APIs are upgraded`, you have to `wait for the HDA` to be updated.

<br>

# Enters Houdini 2 Chat

With Houdini 2 Chat, you have none of these limitations.
- `No need to describe` your network, Houdini 2 Chat does that for you.
- You can use Houdini 2 Chat with almost `any AI Tool` and `any LLM` of your choice.
- New Tools, new LLMs appear every day in this fast paced domain, No need to wait for a new Integration. You can use `New LLMs` as soon as they are available.
- Houdini 2 Chat is `free to use`, also Most powerful AI tools have `free plans`.

## Features
While it is a `proof of concept`, Houdini 2 Chat has the following features today:

- Provides an `LLM Chat ready description` of your Scene
  - Nodes, Parameters
  - Expressions and References
  - User Defined parameters
  - Network Connections, and Loops
  - Sticky Notes and Network Boxes
- Option for `separate files` per Node/per Network Box
- `Filter Scene` Output by specific Nodes/specific Network Boxes
- Works with `any LLM` (Tested with ChatGPT Models, Gemini2, Grok3, Claude 3.7)
- Works with `any AI Code Assistant` (Tested with Github Copilot)
- Works with Special LLM Chat Modes (Tested ChatGPT `Canvas`, Claude `Artifacts`, Google NotebookLM)

## Not yet Implemented
- Limited to Obj Level nodes only.
- Recursive Loops and Recursive Network Boxes
- Networks inside Networks (subnetworks, HDA Networks)
- Full Testing and Evaluation
  
<br>

# Use Cases

- Explain complex Houdini scenes
- Accelerate learning of Houdini
- Get help with coding in VEX, Python, or HScript
- Documentation of Houdini Networks
- Get suggestions to fix problems in Houdini scenes
- Find better workflows from thousands of Houdini Nodes and Parameters you may not know.
 
# How to Install
- Download the latest [HDA](https://github.com/rendermagix/houdini2chat/releases) from the Github [Repo]()
- To install globally, add it in Houdini otls Folder ([Where?](https://www.sidefx.com/docs/houdini/assets/install.html)).

# How to Use
- Open any Houdini Scene, browse to your network
- Drop a Houdini 2 Chat Node
- Hit Export 2 Chat Button.
- Paste the output File(s) in your LLM Chat or link the output folder to your AI Code Assistant for seamless updates.
- Use any of the prompts provided in the output file(s) to get started

> [!NOTE]
> To install the Asset in this Scene only, follow instructions [here](https://www.sidefx.com/docs/houdini/assets/install.html)

# What's Next
- Stabilize it
- Get community feedback
- Develop more features

## Evaluation

Check the [Evaluation](Evaluation.md) document for more details.