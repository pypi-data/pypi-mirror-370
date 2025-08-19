import importlib


def generate_class_code(exchange_name: str):
    try:
        # Dynamically import the module based on the exchange name
        module = importlib.import_module(f"{exchange_name}")
        exchange_methods = module.entries[exchange_name]
    except ImportError:
        raise ValueError(f"Module for exchange '{exchange_name}' could not be found.")
    except AttributeError:
        raise ValueError(f"Entries for exchange '{exchange_name}' not found in the module.")

    class_code = "class ImplicitAPI:\n"

    # Calculate maximum length for method names for alignment
    max_length = 0
    for category, methods in exchange_methods.items():
        for access, http_methods in methods.items():
            if isinstance(http_methods, dict):
                for method, paths in http_methods.items():
                    max_length = max(max_length, *(len(f"{access}_{method}_{path}") for path in paths))
            elif isinstance(http_methods, list):
                max_length = max(max_length, *(len(f"{access}_{path}") for path in http_methods))

    for category, methods in exchange_methods.items():
        class_code += f"\n    # {category} API methods\n"
        for access, http_methods in methods.items():
            class_code += f"\n    # {access} methods\n"
            if isinstance(http_methods, dict):
                for method, paths in http_methods.items():
                    class_code += f"\n    # {method} requests\n"
                    for path in paths:
                        entry_name = f"{access}_{method}_{path}"
                        # Right-align entry names for better readability
                        class_code += f"    {entry_name.ljust(max_length)} = Entry('{category}', '{path}', {{}})\n"
            elif isinstance(http_methods, list):
                for path in http_methods:
                    entry_name = f"{access}_{path}"
                    class_code += f"    {entry_name.ljust(max_length)} = Entry('{category}', '{path}', {{}})\n"

    return class_code


if __name__ == "__main__":
    exchange_names = ["bithumb", "koreainvest", "upbit"]  # List of exchanges to generate files for

    for exchange_name in exchange_names:
        class_code = generate_class_code(exchange_name)
        filename = f"./src/ksxt/api/{exchange_name}.py"
        with open(filename, "w") as file:
            file.write("from ksxt.api import Entry\n")
            file.write("\n")
            file.write(class_code)
