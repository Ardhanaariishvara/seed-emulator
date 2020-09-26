class Printable:
    """!
    @brief Printable class.

    Implement this class for indentable print.
    """

    def print(self, indentation: int = 0) -> str:
        """!
        @brief get printable string.

        @param indentation indentation.

        @returns printable string.
        """

        raise NotImplementedError("print not implemented.")

    def __str__(self) -> str:
        """!
        @brief convert to string.

        alias to print(0).
        """
        return self.print(0)