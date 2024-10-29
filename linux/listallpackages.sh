# ! /bin/bash
# Install essential development packages
# Python interpreter and package manager
sudo apt install -y \
    python3 \                    # Python 3 interpreter
    python3-pip \                # pip package manager for Python 3
    git \                        # Version control system
    curl \                       # Command line tool for transferring data with URL syntax

# Install data science libraries
# Python packages for data analysis and machine learning
pip3 install \
    virtualenv \                 # Tool for creating isolated Python environments 
    conda \                      # Package and environment manager for Python   
    numpy \                      # Numerical computing library
    pandas \                     # Data manipulation and analysis library
    matplotlib \                 # Plotting library
    seaborn \                    # Statistical data visualization
    scikit-learn \               # Machine learning library

    tensorflow \                 # Machine learning framework
    keras \                      # Neural networks library
    torch \                      # Machine learning library
    # opencv-python \              # Open Source Computer Vision Library
    scipy \                      # Scientific computing library
    statsmodels \             # Statistical models library 
    # beautifulsoup4 \          # HTML parser for web scraping 
    # requests \                # HTTP library for making requests 
    # nltk \                    # Natural Language Toolkit 
    # spacy \                   # NLP library 
    # gensim \                  # Topic modeling and document similarity library 
    # networkx \                # Graph theory library 
    # plotly \                  # Interactive plotting library 
    # bokeh \                   # Interactive visualization library 
    # dash \                    # Web application framework 
    # flask \                   # Web application framework 
    # sqlalchemy \              # SQL toolkit and Object-Relational Mapping (ORM) library 
    # psycopg2 \                # PostgreSQL adapter for Python 
    # pymysql \                 # MySQL adapter for Python 
    # sqlalchemy \              # SQL toolkit and Object-Relational Mapping (ORM) library 
    # django \                  # Web framework 
    # fastapi                   # Web framework 

# Additional tools
# Additional software tools
sudo apt install -y \
    htop \                       # Interactive process viewer
    tree \                       # Display directory structure
    cmatrix                      # Console Matrix effect

    echo "Data science packages installation completed."