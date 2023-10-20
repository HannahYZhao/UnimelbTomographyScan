# Tomography Scan
![Example screenshot](Project/img/logo.png)
> This tool's main goal is to assist in the analysis of bone scans through a modular graphical user interface. This tool is to be used for research only and is not to be used for medical purposes.
> Live demo [_here_](https://drive.google.com/file/d/1Bcznd6lfZFtOD1n3N5KmzuQTpSyTM_Qr/view?usp=sharing). <!-- If you have the project hosted somewhere, include the link here. -->

## Table of Contents

* [Installation](#installation)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Usage](#usage)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)
<!-- * [License](#license) -->

## Installation

```bash
git clone https://github.com/robmsharp/tomography-scan.git
cd Project
pip install -r requirements.txt
python landingPage.py
```



## Technologies Used
vtk  9.0.1<br />
PySide2  5.15.2<br />
QtPy  1.9.0<br />
pandas  1.3.3<br />
ryvencore  0.0.2.8<br />
qdarkstyle  3.0.2<br />
slicerSALT
subprocess


## Features
List the ready features here:
- Process builder that user could create their own node to extend
- Process builder brings alignment and visualization functions together, user don't have to switch between those resources 
- User-friendly user interface(dark/light mode, and save user's setting options)


## Screenshots
Switch between dark/light mode.<br />
Process Builder (light mode)
![Example screenshot](Project/img/processBuilder.png)
Process Builder (dark mode)
![Example screenshot](Project/img/processBuilderDark.png)
Visualisation Window (light mode)
![Example screenshot](Project/img/visualisationWindow.png)
Visualisation Window (dark mode)
![Example screenshot](Project/img/visualisationWindowDark.png)
## Usage
**How to create a new node?**
There is a open file node code example.

```python
# A node that allows the user to select a group of VTK files to enter into the 
class FileOpenNode(NodeBase):
    """Select a VTK file / group of VTK files"""

    title = 'Select VTK Files'
    init_outputs = [
        rc.NodeOutputBP(label="Selected files", type_="data")
    ]
    outputTypes = [
        pbutil.FILE_LIST_VTK
    ]
    main_widget_class = FileOpenWidget # The widget this node uses
    main_widget_pos = 'between ports'

    def __init__(self, params):
        super().__init__(params)
        self.val = None
        self.isDataInputNode = True

    def place_event(self): # When placed, update the widget
        self.update()

    # Register the widget for this node
    def view_place_event(self):
        self.main_widget().value_changed.connect(self.main_widget_val_changed)

    # Pass changes from the widget to the node itself
    def main_widget_val_changed(self, val):
        self.val = val
        self.update()

    # Try running this node
    def update_event(self, inp=-1):
        super().update_event(inp)
        if NodeBase.PROCESS_ABLE_TO_RUN:
            if NodeBase.PROCESS_STEP_MODE:
                NodeBase.PROCESS_ABLE_TO_RUN = False

            # Because dataInputNode, always set the output
            self.set_output_val(0, pbutil.getNewTypedData(pbutil.FILE_LIST, self.val))
            print("Files selected count: " + str(len(self.val) if self.val else 0))

```
The two template Nodes are defined in procBuilder/nodes.py <br />

**How to add custom QWidgets for your nodes?** <br />
New widgets can be created and defined in the widgets.py file found in procBuilder. To be displayed on the node, you must set the parameter: main_widget_class = Your Widget and main_widget_pos = "between ports" or "below_ports". You should now be able to see your widget on the node. You can customise the widget however you like using the PySide2 library, such as using it as a trigger to open further dialog boxes or visually modify data etc.

```python
class MyNode(Node):
    main_widget_class = MyNode_MainWidget
    main_widget_pos = 'below ports'  # alternatively 'between ports'
    # ...

```


## Acknowledgements
Give credit here.
- This project was inspired by Ryven 3
- This project was based on [this tutorial](https://ryven.org/).
- Many thanks to our client Big and Kathryn and our supervisor Maria.

- The followings icons were used that required as their license to be acknowledged:

<div>completeIcon.png icon made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com </a></div>
<div>warningIcon.png icon made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com </a></div>
<div>infoIcon.png icon made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com </a></div>
<div>yellow_light.png icon made by <a href="https://www.flaticon.com/authors/pixel-perfect" title="Pixel perfect">Pixel perfect</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com </a></div>



## Contact
| StudentID |       Name       | Github Username |       Role       |
| :-------: | :---------------:|:---------------:| :--------------: |
|  1004285  | John McCleary    | johnmccleary93  | Product Owner    |
|  186477   | Robert Sharp     | robmsharp       | QA lead sprint 1 |
|  1161094  | Hannah Zhao      | HannahYZhao     | VS Developer     |
|  713551   | Jiayu Li         | hedgehog7453    | VS Developer     |
|  1061668  | Jihao Deng       | Declair         | QA lead sprint 2 |
|  912226   | Michael Thomas   | MichaelThomas-1 | Design Architect |
|  835450   | Rohan Jahagirdar | rohanj13        | Scrum Master     |
|  1098403  | Xueqi Guan       | xueqiguan       | VS lead          |
|  1050419  | Yibo Peng        | yibop1050419    | PB Developer     |
|  1006014  | Yuxiang Wu       | WuYuxiang2111   | JiraTask Auditor |
