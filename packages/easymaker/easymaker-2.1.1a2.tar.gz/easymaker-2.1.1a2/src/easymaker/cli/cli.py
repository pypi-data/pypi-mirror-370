import argparse
import os

import easymaker
from easymaker.api.api_sender import ApiSender


def main():
    parser = argparse.ArgumentParser(prog="EasyMaker", description="EasyMaker Command-line interface.")
    parser.add_argument("--version", action="version", version=easymaker.__version__)
    parser.add_argument("--profile", dest="profile", required=False)

    parser.add_argument("--appkey", dest="appkey", required=True)
    parser.add_argument("--region", dest="region", required=True)
    parser.add_argument("--access_token", dest="access_token", required=True)

    parser.add_argument("-instance", dest="instance", action="store_true", help="Supported instance list, usage: python -m easymaker -instance --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-image", dest="image", action="store_true", help="Supported image list, usage: python -m easymaker -image --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-experiment", dest="experiment", action="store_true", help="Experiment list, usage: python -m easymaker -experiment --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-training", dest="training", action="store_true", help="Training list, usage: python -m easymaker -training --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-tuning", dest="tuning", action="store_true", help="Hyperparameter Tuning list, usage: python -m easymaker -tuning --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-model", dest="model", action="store_true", help="Model list, usage: python -m easymaker -model --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-endpoint", dest="endpoint", action="store_true", help="Endpoint list, usage: python -m easymaker -endpoint --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-algorithm", dest="algorithm", action="store_true", help="Algorithm list, usage: python -m easymaker -algorithm --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    parser.add_argument("-model_evaluation", dest="model_evaluation", action="store_true", help="Model Evaluation list, usage: python -m easymaker -model_evaluation --appkey APPKEY --region REGION --access_token ACCESS_TOKEN")

    args = parser.parse_args()

    region = args.region
    appkey = args.appkey
    access_token = args.access_token
    if args.profile:
        os.environ["EM_PROFILE"] = args.profile

    api_sender = ApiSender(region, appkey, access_token)

    if args.instance:
        for item_list in api_sender.get_instance_type_list():
            print(item_list["name"])
    elif args.image:
        for item_list in api_sender.get_image_list():
            print(item_list["name"])
    elif args.experiment:
        for item_list in api_sender.get_experiment_list():
            print(f"Experinemt Name : {item_list['name']}, Experinemt ID : {item_list['id']}")
    elif args.training:
        for item_list in api_sender.get_training_list():
            print(f"Training Name : {item_list['name']}, Training ID : {item_list['id']}")
    elif args.tuning:
        for item_list in api_sender.get_hyperparameter_tuning_list():
            print(f"Hyperparameter Tuning Name : {item_list['name']}, Hyperparameter Tuning ID : {item_list['id']}")
    elif args.model:
        for item_list in api_sender.get_model_list():
            print(f"Model Name : {item_list['name']}, Model ID : {item_list['id']}")
    elif args.endpoint:
        for item_list in api_sender.get_endpoint_list():
            print(f"Endpoint Name : {item_list['name']}, Endpoint ID : {item_list['id']}")
    elif args.algorithm:
        for item_list in api_sender.get_algorithm_list():
            print(f"Algorithm Name : {item_list['name']}, Algorithm ID : {item_list['id']}, Available Training Images: {item_list['availableTrainingImageList']}")
    elif args.model_evaluation:
        for item_list in api_sender.get_model_evaluation_list():
            print(f"Model Evaluation Name : {item_list['name']}, Model Evaluation ID : {item_list['id']}")


if __name__ == "__main__":
    main()
