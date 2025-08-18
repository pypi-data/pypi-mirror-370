# Contribute

Create an environment and install the dev dependencies:
```bash
conda create -n agent-sdk python=3.10

pip install .[dev]
```

Run black formatting on the code:
```bash
black .
```

### Generating Documentation

If you'd like to generate the pydoc documentation for the project, you can use the following command. This will create HTML documentation for all the Python modules:

```bash
find src -name "*.py" | sed 's|src/||; s|/__init__.py||; s|.py$||; s|/|.|g' | xargs -I {} python -m pydoc -w {} && mv *.html docs/
```

This command:

1. **Searches** for all `.py` files in the `src` directory.
2. **Converts** file paths into Python module paths (e.g., `src/fabric/dataagent/client.py` becomes `fabric.dataagent.client`).
3. **Generates** HTML documentation for each module.
4. **Moves** the generated `.html` files into the `docs/` directory.


If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:

- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)


## Create an ADO Package Feed PAT (Personal Access Token)

To create a PAT go to https://dev.azure.com/msdata/A365/_artifacts/feed/synapseml-agent-sdk. Make sure to add the `Packaging` to the scope. 

Create & export PIP_INDEX_URL URL. This allows you to fetch all packages only from internal feed. You will need an Azure DevOps PAT (Personal Access Token). 
([How to get an ADO PAT ?]
(https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?toc=%2Fazure%2Fdevops%2Forganizations%2Fsecurity%2Ftoc.json&view=azure-devops&tabs=Windows#create-a-pat))

For Linux:

```bash
export PAT='<YOUR-ADO-PACKAGE-FEED-READ-ONLY-TOKEN-AS-BARE-STRING>'
export PIP_INDEX_URL="https://Synapse-Conda:$PAT@msdata.pkgs.visualstudio.com/A365/_packaging/synapseml-agent/pypi/simple/"
export PIP_EXTRA_INDEX_URL="https://Synapse-Conda:$PAT@msdata.pkgs.visualstudio.com/A365/_packaging/SynapseML-Enya/pypi/simple/"
```

For Windows:

```cmd
set PAT='<YOUR-ADO-PACKAGE-FEED-READ-ONLY-TOKEN-AS-BARE-STRING>'
set PIP_INDEX_URL=https://Synapse-Conda:%PAT%@msdata.pkgs.visualstudio.com/A365/_packaging/synapseml-agent/pypi/simple/
set PIP_EXTRA_INDEX_URL=https://Synapse-Conda:%PAT%@msdata.pkgs.visualstudio.com/A365/_packaging/SynapseML-Enya/pypi/simple/
```

## Build and Test

```bash
conda create -n agent-sdk python=3.10

pip install -e ".[test]"

pytest -s tests
```

## Integration tests

```bash
ut_workspace='Data Agent v2 Streaming Files' pytest -s tests/ -v
```

## Build package

```bash
pip install build
python -m build

azcopy copy "dist/fabric_data_agent_sdk*" "https://marcozo.blob.core.windows.net/public"
```

## Release
- Tag the main branch with the version number (ex: git tag 0.0.1)
- Push the tag to the remote repository (ex: git push origin 0.0.1)
- Run [SynapseML Agent SDK Release](https://msdata.visualstudio.com/A365/_build?definitionId=45583) against the tag