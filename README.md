
# Calphad

calphad is a python based library which allows user to generate phase diagrams of different alloys using calphad calculation. This library can be used in python script or directly in command promt where the calculation can be done by using simple UI. The data used for this module is thermodynamical database(.tdb/.TDB)


## Functions

### data_reader()
`data_reader()` is a function which creates class object and can be used further as data.

    from data_reader import data_reader
    data = data_reader() #<-- This will be data object

### scan_data()
`scan data()` is a function with in data_reader class used to scan data from a .tdb file.
It takes file_name as input argument where direct path of the file also can be used.

    data.scan_data(file_name = 'example_data.tdb')

### select_element()
`select_element()` is a function in calphad module which shows available elements in data and allows user to select elements with desired compositions accordingly. It takes data_reader object as input argument to process the data.
The available element information will be shown in the kernal where user is able to select and give composition. It returns 2 variables as elements list and respected composition.

    from calphad import select_element
    elements, composition = select_element(data)

### grab_phases()
`grab_phases()` is a function which takes selected elements list and data_reader object as input arguments and shows posible phases occurs in the alloy and returns a list of phase names.

    from calphad import grab_phases
    phases = grab_phases(elements, data)

### select_phases()
`select_phases()` is a function which allows user to select phases which are needed to be calculated. It takes phases list and data_reader object as input argument and returns list of selected phases.

    from calphad import select_phases
    selected_phases = select_phases(phases, data)

### create_phases()
`create_phases()` is a function which creates phase objects which are further used in calphad calculation. The function takes selected phases list, data_reader object, elements list and compositon as input and returns list phase objects.

    from calphad import create_phases()
    phase_objects = create_phases(selected_phases, data, elements, composition)



## Acknowledgements

At present this modules are only capable of fetching and processing datafrom thermodynamical database, able to detect required values for phase calculation and calculate phase energy at desired temperature. However more futures like simulation of phase equilibrium and rendering phase diagram will be added in the future. 


## License

[GNU GPL](https://choosealicense.com/licenses/gpl-3.0/)


## Authors

- [@rohithandanala](https://github.com/rohithandanala)

