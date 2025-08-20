class StiElement:

### Properties
    
    id: str = None
    """Gets or sets the component or element ID that will be used for the name of the object when preparing JavaScript code."""

    htmlRendered: bool = False


### HTML

    def getHtml(self) -> str:
        """
        Gets the HTML representation of the element.
        
        return:
            Prepared HTML and JavaScript code for embedding in an HTML template.
        """

        self.htmlRendered = True
        return ''
    