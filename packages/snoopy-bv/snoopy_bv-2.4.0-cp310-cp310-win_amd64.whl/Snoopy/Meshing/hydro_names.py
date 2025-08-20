from math import floor, log10, ceil
DOF   = ["surge","sway","heave","roll","pitch","yaw"]


def get_full_dataname(data_name,data_type,frequency,heading):
    """Provide a name to the field from metadata.

    Parameters
    ----------
    data_name : str
        Type or data (PRESSURE_RAD, PRESSURE_DIF...)
    data_type : int
        Component of the data
    frequency : float
        frequency
    heading : float
        heading

    Returns
    -------
    str
        full field name
    """
    index_mode = floor(data_type/2)
    is_real = (data_type % 2 == 0)

    # Name of the dof, followed by teh body number. 
    dof_name = f"{DOF[index_mode%6]:}{floor(index_mode/6)+1:}"

    if data_name.endswith("RAD") :
        name = f"{data_name}_{dof_name:}_HEAD_{heading:.1f}_FREQ_{frequency:.4f}"
    elif data_name[-3:] in ["EXC", "DIF", "INC"] or data_name.endswith("TOTAL"):
        name = f"{data_name}_HEAD_{heading:.1f}_FREQ_{frequency:.4f}"
    elif data_name[-3:] in ["DBD","STD"]:
        name = f"{data_name}_{dof_name}"
    else:
        return data_name
    if is_real:
        name += "_RE"
    else:
        name += "_IM"
    return name


def get_full_dataname_metadata(metadata):
    nbdata = len(metadata)
    nbspace = ceil(log10(nbdata))
    list_name = []
    for irow, row in metadata.iterrows():
        id = str(irow).zfill(nbspace)
        list_name.append(id +"_" +
            get_full_dataname(row.data_name,row.data_type,row.frequency,row.heading) )
    return list_name
    
        


if __name__ == "__main__":
    
    
    print(get_full_dataname("PRESSURE_RAD", data_type=23, frequency = 0.5 , heading = 180))