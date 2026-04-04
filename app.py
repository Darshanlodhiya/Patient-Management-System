from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field
from typing import Literal
import pickle
import pandas as pd