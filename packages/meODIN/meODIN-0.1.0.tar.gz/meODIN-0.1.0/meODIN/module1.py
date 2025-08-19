import numpy as np

class Math:
    """
    A collection of utility methods for converting optical parameters related to
    irregularity and power in interferometry.
    """

    @staticmethod
    def irrFrToMm(fringes, wavelength_nm):
        """
        Convert irregularity from fringes to millimeters.

        Parameters:
            fringes (float): Number of fringes.
            wavelength_nm (float): Wavelength in nanometers.

        Returns:
            float: Irregularity in millimeters.
        """
        wavelength_mm = wavelength_nm * 1e-6
        return fringes * (wavelength_mm / 2)

    @staticmethod
    def irrMmToFr(irregularity_mm, wavelength_nm):
        """
        Convert irregularity from millimeters to fringes.

        Parameters:
            irregularity_mm (float): Irregularity in millimeters.
            wavelength_nm (float): Wavelength in nanometers.

        Returns:
            float: Number of fringes.
        """
        wavelength_mm = wavelength_nm * 1e-6
        return irregularity_mm / (wavelength_mm / 2)
    
    @staticmethod
    def powFrToMm(diameter_mm, nominal_radius_mm, surface_type, fringes, wavelength_nm):
        """
        Estimate effective radius from power fringes using nominal radius and lens type.

        Parameters:
            diameter_mm (float): Lens diameter in mm.
            nominal_radius_mm (float): Nominal radius of curvature in mm.
            surface_type (str): "CC" for concave or "CX" for convex.
            fringes (float): Number of fringes.
            wavelength_nm (float): Wavelength in nanometers.

        Returns:
            float: Corrected radius of curvature in mm.
        """
        if surface_type == "CC":
            index = 1
        elif surface_type == "CX":
            index = -1
        else:
            raise ValueError("surface_type must be 'CC' or 'CX'")

        h_mm = 0.5 * (2 * nominal_radius_mm - np.sqrt(4 * nominal_radius_mm**2 - diameter_mm**2))
        power_mm = (index * fringes / 2) * (wavelength_nm * 1e-6)
        return (diameter_mm**2 + 4 * (h_mm + power_mm)**2) / (8 * (h_mm + power_mm))
    
    @staticmethod
    def powMmToFr(diameter_mm, nominal_radius_mm, surface_type, power_mm, wavelength_nm):
        """
        Estimate number of fringes from power in mm using nominal radius and lens type.

        Parameters:
            diameter_mm (float): Lens diameter in mm.
            nominal_radius_mm (float): Nominal radius of curvature in mm.
            surface_type (str): "CC" for concave or "CX" for convex.
            power_mm (float): Sag difference due to power in mm.
            wavelength_nm (float): Wavelength in nanometers.

        Returns:
            float: Number of power fringes.
        """
        if surface_type == "CC":
            index = 1
        elif surface_type == "CX":
            index = -1
        else:
            raise ValueError("surface_type must be 'CC' or 'CX'")

        # Calculate sag from nominal radius
        h_mm = 0.5 * (2 * nominal_radius_mm - np.sqrt(4 * nominal_radius_mm**2 - diameter_mm**2))

        # Intermediate value from Rc equation
        term = power_mm - 0.5 * np.sqrt(4 * power_mm**2 - diameter_mm**2)

        # Power contribution in mm
        power_mm = term - h_mm

        # Convert power in mm to fringes
        fringes = (2 * power_mm) / (index * wavelength_nm * 1e-6)
        return fringes


    @staticmethod
    def randomValue(distribution="uniform"):
        """
        Generate a random value between -1 and 1 based on a distribution.

        Parameters:
            distribution (str): One of 'uniform', 'gauss', or 'parabolic'.

        Returns:
            float: Random value in [-1, 1].
        """
        if distribution == "uniform":
            return np.random.uniform(-1, 1)

        elif distribution == "gauss":
            while True:
                value = np.random.normal(0, 0.5)
                if -1 <= value <= 1:
                    return value

        elif distribution == "parabolic":
            while True:
                x = np.random.uniform(-1, 1)
                y = np.random.uniform(0, 1)
                if y <= (3 * x**2) / 2:
                    return x

        else:
            raise ValueError("Invalid distribution type. Choose 'uniform', 'gauss', or 'parabolic'.")
