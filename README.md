# ursa major

A microservice to discover and store bags.

ursa major is part of [Project Electron](https://github.com/RockefellerArchiveCenter/project_electron), an initiative to build sustainable, open and user-centered infrastructure for the archival management of digital records at the [Rockefeller Archive Center](http://rockarch.org/).

[![Build Status](https://travis-ci.org/RockefellerArchiveCenter/ursa_major.svg?branch=base)](https://travis-ci.org/RockefellerArchiveCenter/ursa_major)
![GitHub (pre-)release](https://img.shields.io/github/release/RockefellerArchiveCenter/ursa_major/all.svg)

## Setup

Install [git](https://git-scm.com/) and clone the repository

    $ git clone https://github.com/RockefellerArchiveCenter/ursa_major.git

Install [Docker](https://store.docker.com/search?type=edition&offering=community) and run docker-compose from the root directory

    $ cd ursa_major
    $ docker-compose up

Once the application starts successfully, you should be able to access the application in your browser at `http://localhost:8005`

When you're done, shut down docker-compose

    $ docker-compose down

Or, if you want to remove all data

    $ docker-compose down -v


## Services

ursa major has four services, all of which are exposed via HTTP endpoints (see [Routes](#routes) section below):

* Store Accessions - validates incoming data, and saves an Accession object as well as a Bag object for each transfer identified in the `transfers` key of the data delivered.
* Bag Discovery - the main service for this application, which consists of the following steps:
  * Checking to see if the files for the bag are in the landing directory.
  * "Unpacking" the bag files and saving the metadata to the Bag object.
  * Moving bag to the storage directory and updating the `bag_path` field.
* Bag Delivery - delivers data about the bag to another service.
* Cleanup - removes files from the destination directory.


### Routes

| Method | URL | Parameters | Response  | Behavior  |
|--------|-----|---|---|---|
|POST|/accessions||200|Creates accession objects as well as associated bags|
|GET|/bags| |200|Returns a list of transfers|
|GET|/bags/{id}| |200|Returns data about an individual transfer|
|POST|/bagdiscovery||200|Runs the BagDiscovery routine|
|POST|/bagdelivery||200|Runs the BagDelivery routine|
|POST|/cleanup||200|Runs the Cleanup routine|
|GET|/status||200|Return the status of the microservice|
|GET|/schema.json||200|Returns the OpenAPI schema for this application|



## Development

This repository contains a configuration file for git [pre-commit](https://pre-commit.com/) hooks which help ensure that code is linted before it is checked into version control. It is strongly recommended that you install these hooks locally by installing pre-commit and running `pre-commit install`.


## License

This code is released under an [MIT License](LICENSE).
