# Infrastructure as Code

We follow a form of `Infrastructure as Code` where all of our cloud based infrastructure is set up using a declarative format and tools that handle the implementation.

Our clients will each use their own cloud provider and we need to ensure that we are able to manage these different environments in a secure and scalable way. To enable this we use HashiCorp's Terraform to define the infrastructure. The project will host its `Infrastructure as Code` in a separate repository which can be found [here](fake URL).

And extension of `Infrastructure as Code` is called `Policy as Code`. This allows for security and compliance to be declared and enforced using software, instead of going through long text based guides in a manual procedure.

### Building Single File Executables for different Operating Systems

The building of a single file executable which can be run on MacOS, Linux, and Windows is handled as part of the CI/CD process using Github Actions. 

These will be automatically built and uploaded for each release of the project. See the project `README.md` for further details on the specific release process.

The building a a single file exectuable uses the [Nuitka Python tool](https://nuitka.net/) and associated Github Action.