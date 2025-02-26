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
- Works with `any LLM` (Tested with ChatGPT Models, Gemini2, Grok3, Claude 3.7)
- Works with `any AI Code Assistant` (Tested with Github Copilot)
- Works with Special LLM Chat Modes (Tested ChatGPT `Canvas`, Claude `Artifacts`, Google NotebookLM)
- Option for `separate files` per Node/per Network Box
- `Filter Scene` Output by specific Nodes/specific Network Boxes

## Not yet Implemented
- Limited to Obj Level nodes only.
- Recursive Loops and Recursive Network Boxes
- Networks inside Networks (subnetworks, HDA Networks)
- Full Testing and Evaluation
  
<br>

# Does it really work?

## Evaluation Criteria
Evaluation criteria is based on LLM/AI Tool ability to recognize the following:

- Understanding the Scene Representation:
  - Nodes and their connections
  - Network Structure
    - Branches In/Out
    - Loops
    - Network Boxes/Sticky Notes
  - Node Parameters
    - Values/Expressions/References
    - User Defined, defaults
- Understanding the Scene Logic:
  - Nodes meaning and purpose
  - Network Logic and Purpose
- Visualization:
  - Visualizing the Output
  - Visualizing Animation
  - Visualizing Geometry
- Working seamlessly across LLMs/AI Tools
  - Try Multiple LLMs with same prompts
  - Try Multiple AI Tools with same prompts
  - Get acceptable results with Regular and Thinking Models

<br>

>[!NOTE]
> To ensure LLM didn't train on these specific scenes, we stripped identifying information from scene descriptions for some of them. We will provide later evaluation of non public scenes that we tested internally.

## Scene Credits
We have picked some of the most popular Houdini Tutorials and Examples to evaluate Houdini 2 Chat. We have made minor changes to a few of the scenes to demonstrate some capabilities or overcome known limitations.
Full credit to the following Channels/Authors for providing these scenes to the Houdini Community. I have greatly learned from each one of them.
- [CGWiki](https://tokeru.com/cgwiki/)
- [Mr. Junichiro Horikawa](https://www.youtube.com/@junichirohorikawa)
- [Entagma](https://www.youtube.com/@entagma)
- [Simple and Procedural](https://www.youtube.com/@simpleandprocedural)


## Evaluation

### 1. xyzdist Demo

<table>
  <tr>
    <td><img src="images/xyzdist.gif" alt="img" width="400"/></td>
    <td><img src="images/xyzdist_net.JPG" alt="network" width="400"/></td>
  </tr>
</table>

This is the simplest demo that demonstrates a point orbiting around a 3d Surface.
> xyzdist finds the distance, primnum, uv of the closest prim, a point is made at that location, its colour is set from the closest prim, a red line is drawn from the orbiting point to the new point, and finally a wireframe sphere is generated on the new point, its colour also matches the prim its currently on, and its radius is set from the distance returned from xyzdist, so it alwasy just touches the orbiting point.

Extract from Claude Analysis:

![Claude](images/1_res1.JPG)