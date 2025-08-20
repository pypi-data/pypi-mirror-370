version: "3.9"
name: $stack_name

services:
  $validators
  app:
    container_name: $val_name
    environment:
      PYTHONUNBUFFERED: "1"
      PYTHONDONTWRITEBYTECODE: "1"
