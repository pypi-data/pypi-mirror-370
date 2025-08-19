Luminary Cloud's Python Software Development Kit (SDK) allows you to access many of the features within our platform programmatically (i.e. without needing to go through the graphical user interface in your browser).

Our Python SDK provides a secure abstraction layer, a set of simulation-specific data structures, and all the necessary functionality to enable automation via simple Python scripts.

It allows you to create your own applications leveraging Luminary (such as importing geometry and creating meshes, running and post-processing simulations, running explorations and creating surrogate models) and connect Luminary simulations to pre- and post-processing tools that are already part of your own workflows.

The sample code below shows how the SDK can be used to upload a mesh and run a
simulation (note that the Python SDK is designated as Early Access and syntax
and functionality may change significantly).

```py
import luminarycloud as lc
project = lc.create_project("NACA 0012", "My first SDK project.")
mesh = project.upload_mesh("./airfoil.lcmesh")
sim_template = project.create_simulation_template("test template", params_json_path="./simulation_template.json")
sim = project.create_simulation(mesh.id, "My simulation", sim_template.id)
```
