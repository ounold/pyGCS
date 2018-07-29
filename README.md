# pyGCS
Repository containing implementation of Stochastic Grammar-based Classifier System in Python (pyGCS).

## Requirements
To run library you have to had installed some dependencies:
* _**Python**_ (>= 3.6.3) - major environemnt to run library
* _**Jupyter**_ (>= 4.4.0) - notebook to run library and visualize results
* _**Networkx**_ (>= 2.1) - python library for BSF tree
* _**Jsonpickle**_ (>= 0.9.6)- serializing python objects to json objects
* _**Numpy**_ (>= 1.14.1) - fundamental package for scientific computing

## Running
To run pyGCS library you have to follow one of some methods.
All library parameters are available from file app.ini
~~~
Grammar/app.ini
~~~
### Console line without Jupyter
Go to main app directory
~~~
cd Grammar
~~~
Next run python3 app with following parameters
~~~python
python3 main.py app.ini logger.ini
~~~

### Console line with Jupyter
Go to main app directory
~~~
cd Grammar
~~~
Next run jupyter app with following parameters
~~~python
jupter notebook
~~~
Jupyter notebook will be accesed on webpage
~~~
http://localhost:8888
~~~
All charts and graphs will be available on
~~~
http://localhost:8000
~~~

### Docker
First you have to had installed
* Docker (>= 18.03) - virtual operational system
* Docker Compose (>= 1.21.1) - manager images and conatiners

From root directory run build command
~~~
docker-compose build gcs
~~~
To run pyGCS library run
~~~
docker-compose up -d gcs
~~~
Jupyter notebook will be access on webpage
~~~
http://localhost:8888
~~~
All charts and graphs will be available on
~~~
http://localhost:8000
~~~

## Results
Library after induction saving results to data folder
~~~
cd ../Charts/data
~~~
