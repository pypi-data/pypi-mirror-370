"""
Collection of useful simulation utilities
"""


def check_contact(sim, geoms_1, geoms_2=None):
    """
    Finds contact between two geom groups.
    Args:
        sim (MjSim): Current simulation object
        geoms_1 (str or list of str): an individual geom name or list of geom names
        geoms_2 (str or list of str or None): another individual geom name or list of geom names.
            If None, will check any collision with @geoms_1 to any other geom in the environment
    Returns:
        bool: True if any geom in @geoms_1 is in contact with any geom in @geoms_2.
    """
    # Check if either geoms_1 or geoms_2 is a string, convert to list if so
    if type(geoms_1) is str:
        geoms_1 = [geoms_1]
    if type(geoms_2) is str:
        geoms_2 = [geoms_2]
    for i in range(sim.data.ncon):
        contact = sim.data.contact[i]
        # check contact geom in geoms
        c1_in_g1 = sim.model.geom_id2name(contact.geom1) in geoms_1
        c2_in_g2 = (
            sim.model.geom_id2name(contact.geom2) in geoms_2
            if geoms_2 is not None
            else True
        )
        # check contact geom in geoms (flipped)
        c2_in_g1 = sim.model.geom_id2name(contact.geom2) in geoms_1
        c1_in_g2 = (
            sim.model.geom_id2name(contact.geom1) in geoms_2
            if geoms_2 is not None
            else True
        )
        if (c1_in_g1 and c2_in_g2) or (c1_in_g2 and c2_in_g1):
            return True
    return False
