from letschatty.models.company.assets.product import Product

class ProductFactory:

    @staticmethod
    def create_product(dict_product: dict) -> Product:
        clean_dict_product = {}
        name = dict_product.get("name")
        if not name:
            raise ValueError("Name is required")
        clean_dict_product["name"] = name
        company_id = dict_product.get("company_id")
        if not company_id:
            raise ValueError("Company ID is required")
        clean_dict_product["company_id"] = company_id
        base_fields = ["name", "price", "information", "external_id", "color", "parameters", "company_id", "created_at", "updated_at", "deleted_at", "id"]
        parameters = dict_product.get("parameters")
        if parameters and not isinstance(parameters, dict):
            raise ValueError("Parameters field must be a dictionary")
        if parameters:
            clean_dict_product["parameters"] = parameters
        else:
            clean_dict_product["parameters"] = {}

        for field in dict_product:
            if field and field not in base_fields:
                clean_dict_product["parameters"][field] = dict_product.get(field)
            elif field in base_fields:
                clean_dict_product[field] = dict_product.get(field)

        return Product(**clean_dict_product)
