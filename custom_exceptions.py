class DataNotLoadedError(ValueError):
    """Raised when the data is not loaded."""
    def __init__(self, data, message="Please load the data using DataLoader.load_data() method."):
        self.data = data
        self.message = message
        super().__init__(self.message) # Call the parent class constructor

    def __str__(self):
        return f"data = {self.data} -> {self.message}" # Customize the error message display