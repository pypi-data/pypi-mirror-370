# EnviDat Converters
This project features converters made for [EnviDat](https://www.envidat.ch/) metadata.
- EnviDat to JSON-LD
- EnviDat to DataCite XML
- EnviDat to RIS
- EnviDat to DIF
- EnviDat to ISO 19139
- EnviDat to BIBTEX
- EnviDat to DCAT-AP
- EnviDat to Signposting

It also offers a way to download EnviDat metadata.

## So how do I use it?

All you need to do is install the package.

Clone the repository in a folder of your choosing. Then install it. Easy!

We recommend using a virtual environment as described here, but in theory you can also just run the last command.

```
# Create virtual environment:
python -m venv <virtual-environment-name>

# Activate virtual environment (depends on your OS)
# Linux/MacOS
source <virtual-environment-name>\bin\activate
# Windows
<virtual-environment-name>\Scripts\activate.bat

# Install the package.
pip install .
```

If you have set this up before and come back to the project at a different time, the only step you need to do is activate the virtual environment.

Once this project is on PyPi, I will add the according instructions here.


## Command Line Usage

<details> 

<summary>Command Line Usage</summary>

Open your favourite terminal.
So far, you have two main functionalities:
- Getting the metadata directly from EnviDat
- Converting that metadata to a format of your choosing

Both have the option to either just print the output or save it as a file.

### EnviDat metadata

To show or download the metadata, use the following command:

`(python) envidat-converter get-data <query>`

Query is your search term. It can be a *DOI*, a *dataset name* or a *dataset ID*.

**Optional**:

To download the dataset, use the --download flag. This will save the file in your current directory.

If you want to specify the path, you can do that with the --outputdir flag.

**Examples**:

`(python) envidat-converter get-data labes`

... will print the dataset with the name "labes" in your terminal.

`(python) envidat-converter get-data "10.16904/envidat.228" --download --outputdir ".\foldername"`

... will save the dataset with the DOI 10.16904/envidat.228 in a new folder called "foldername".


### Convert metadata

So far you can convert to the following formats:
- Datacite (XML)
- Json LD in the style of Zenodo (JSON)

To use the converter, use:

`(python) envidat-converter convert <query> --converter <converter>`

Let's break that down:
- query: query is your search term. It can be a *DOI*, a *dataset name* or a *dataset ID*.
- converter: this can currently be "datacite", "jsonld", "bibtex", "dif", "ris", "iso", or "dcatap"

**Optional**:

To download the dataset, use the --download flag. This will save the file in your current directory.

If you want to specify the path, you can do that with the --outputdir flag.

**Examples**:

`(python) envidat-converter convert labes --converter datacite`

... will print the dataset with the name "labes" in the datacite format in your terminal.

`(python) envidat-converter convert "10.16904/envidat.228" --converter jsonld --download --outputdir ".\foldername"`

... will save the dataset with the DOI 10.16904/envidat.228 in a new folder called "foldername".

</details>

## API usage
<details>

<summary>API usage</summary>

Make sure you have uvicorn installed. Then it's as simple as running

`uvicorn converters.main:app --port 8080`


It should load up under http://localhost:8080/. Note that you can always change the port number to whatever fits your needs.

The docs should open up and help you use the API.

- To convert metadata, use the convert-metadata endpoint. You can use IDs, package names, or DOIs as query.
- To simply get the EnviDat metadata, use the get-data endpoint. You can use IDs, package names, or DOIs as query.
</details>

## Addtional information

This repository was tested against Python Versions 3.8, 3.9, 3.10, 3.11, 3.12, 3.13. Version 3.8 and 3.9 did not work due to dependency issues. 

### config.ini
If you are not just handling production data but, for example, have a local database that you want to test, you can add the environment to config.ini. There is no need to restart or reinstall after making changes.