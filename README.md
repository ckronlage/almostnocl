## just open the viewer

### Motivation
A lot of interesting open-source research software in neuroimaging is being developed and published. Many projects have concrete clinical applications, e.g., volumetry to measure neurodegeneration, detection or segmentation of pathologies like tumours. For guiding development toward real clinical needs, feedback from clinicians is valuable, especially when they are able to test new tools using their own data. However, research software often requires time-consuming and complex setup, while transferring clinical data is often not permitted.

### Idea
Make the setup and demo of different research neuroimaging tools as easy as possible, to enable users to run these locally on own data.
More recent developements that we can make use of include:
- Deep learning tools that often run in seconds (GPU) or minutes (CPU) instead of hours
- Software containerization (docker etc.)
- [NiiVue](https://niivue.com/), a polished in-browser viewer for 3D medical images
Optimally, the user experience should only require installing Docker and then look like this:
<img width="600" alt="pitch_figure" src="https://github.com/user-attachments/assets/c6ce03f9-9430-4ba1-b0bd-a4068a85d25e" />

### Current status
We have (half vibe-)coded a minimal template and a version with synthseg to display a hippocampal segmentation. This is overall less than 1000 lines of code (python, HTML, Dockerfile).

You need docker, raise the system memory limit to >16GB and then do:
```
git clone -b synthseg https://github.com/ckronlage/nii_proc_gui
cd nii_proc_gui
docker compose up
```
And go to (http://localhost:8000)

<img width="600" src="https://github.com/user-attachments/assets/10e2e430-1cd8-4563-a53d-179a32c2f83b" />


### Goals
- Keep the code as short and minimal as possible, making it easier maintain and adapt for new tools
- Improvements to the template (e.g., DICOM input support, UI)
- Test on different OSs (Linux, Mac, Windows) and test GPU support for some deep learning tools
- Making separate versions for different tools with optimized viewer UI for each one, e.g.:
    - Hippocampal volumetry with synthseg
    - nnUNet for different segmentation tasks
    - Perhaps something you have developed?

We know that there is for example [NiiVue-Fullstack](https://github.com/niivue/fullstack-niivue-demo), which can be hosted in a cloud on the web, and is therefore much more complex (user management, authentication). This is meant to be simple, easy, and run locally.

### About us
- We are from the [IMAGINE lab](https://imaginelab.github.io/) at King's College London, we usually work on developing tools for improving clinical diagnosis in epilepsy. The idea for this project is inspired by interactions with clinical colleagues in radiology, neurology and paediatrics.
- We are just dabbling in web app design and would like to learn a little bit through this project - if you're knowledgeable, please join and show us how it's done :)
