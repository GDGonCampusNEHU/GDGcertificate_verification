import os
from flask import Flask, render_template, abort, request
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid