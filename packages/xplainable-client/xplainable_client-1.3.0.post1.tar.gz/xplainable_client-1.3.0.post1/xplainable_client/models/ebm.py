
class EBMMetadataTransformer:
    @staticmethod
    def transform_ebm_metadata(ebm_model):
        profile = {
            "base_value": ebm_model.intercept_[0],
            "categorical": {},
            "numeric": {}
        }

        feature_importances = []

        for feature_name, feature_group in ebm_model.explain_global().data(0):
            if feature_group["type"] == "categorical":
                categories = []
                for category in feature_group["names"]:
                    category_index = feature_group["names"].index(category)
                    categories.append({
                        "category": category,
                        "score": feature_group["scores"][category_index],
                        "mean": None,
                        "freq": None
                    })
                categories.append({
                    "category": None,
                    "score": 0,
                    "mean": 0,
                    "freq": 0
                })
                profile["categorical"][feature_name] = categories
            elif feature_group["type"] == "continuous":
                bins = []
                for i in range(len(feature_group["names"])):
                    bins.append({
                        "lower": feature_group["names"][i][0],
                        "upper": feature_group["names"][i][1],
                        "score": feature_group["scores"][i],
                        "mean": None,
                        "freq": None
                    })
                bins.append({
                    "lower": None,
                    "upper": None,
                    "score": 0,
                    "mean": 0,
                    "freq": 0
                })
                profile["numeric"][feature_name] = bins

            feature_importances.append({
                "name": feature_name,
                "value": feature_group["importance"]
            })

        return profile, feature_importances
    

class EBMMetadataTransformer:
    @staticmethod
    def transform_ebm_metadata(ebm_model):
        profile = {
            "base_value": ebm_model.intercept_[0],
            "categorical": {},
            "numeric": {}
        }

        feature_importances = []

        for feature_name, feature_group in ebm_model.explain_global().data(0):
            if feature_group["type"] == "categorical":
                categories = []
                for category in feature_group["names"]:
                    category_index = feature_group["names"].index(category)
                    categories.append({
                        "category": category,
                        "score": feature_group["scores"][category_index],
                        "mean": None,
                        "freq": feature_group["percents"][category_index]
                    })
                categories.append({
                    "category": None,
                    "score": 0,
                    "mean": 0,
                    "freq": 0
                })
                profile["categorical"][feature_name] = categories
            elif feature_group["type"] == "continuous":
                bins = []
                for i in range(len(feature_group["names"])):
                    bins.append({
                        "lower": feature_group["names"][i][0],
                        "upper": feature_group["names"][i][1],
                        "score": feature_group["scores"][i],
                        "mean": None,
                        "freq": feature_group["percents"][i]
                    })
                bins.append({
                    "lower": None,
                    "upper": None,
                    "score": 0,
                    "mean": 0,
                    "freq": 0
                })
                profile["numeric"][feature_name] = bins

            feature_importances.append({
                "name": feature_name,
                "value": feature_group["importance"]
            })

        return profile, feature_importances