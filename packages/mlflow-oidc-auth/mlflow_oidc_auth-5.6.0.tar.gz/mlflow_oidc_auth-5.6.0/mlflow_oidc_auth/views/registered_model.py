from flask import jsonify, make_response
from mlflow.server.handlers import _get_model_registry_store, catch_mlflow_exception

from mlflow_oidc_auth.responses.client_error import make_forbidden_response
from mlflow_oidc_auth.store import store
from mlflow_oidc_auth.utils import (
    can_manage_registered_model,
    check_registered_model_permission,
    fetch_all_registered_models,
    get_is_admin,
    get_request_param,
    get_username,
)


@catch_mlflow_exception
@check_registered_model_permission
def create_registered_model_permission(username: str, name: str):
    store.create_registered_model_permission(
        name=name,
        username=username,
        permission=get_request_param("permission"),
    )
    return jsonify({"message": "Model permission has been created."})


@catch_mlflow_exception
@check_registered_model_permission
def get_registered_model_permission(username: str, name: str):
    rmp = store.get_registered_model_permission(name=name, username=username)
    return make_response({"registered_model_permission": rmp.to_json()})


@catch_mlflow_exception
@check_registered_model_permission
def update_registered_model_permission(username: str, name: str):
    store.update_registered_model_permission(
        name=name,
        username=username,
        permission=get_request_param("permission"),
    )
    return make_response(jsonify({"message": "Model permission has been changed"}))


@catch_mlflow_exception
@check_registered_model_permission
def delete_registered_model_permission(username: str, name: str):
    store.delete_registered_model_permission(name=name, username=username)
    return make_response(jsonify({"message": "Model permission has been deleted"}))


# TODO: refactor it, move filtering logic to the store
@catch_mlflow_exception
def list_registered_models():
    if get_is_admin():
        registered_models = fetch_all_registered_models()
    else:
        current_user = store.get_user(get_username())
        registered_models = []
        for model in fetch_all_registered_models():
            if can_manage_registered_model(model.name, current_user.username):
                registered_models.append(model)
    models = [
        {
            "name": model.name,
            "tags": model.tags,
            "description": model.description,
            "aliases": model.aliases,
        }
        for model in registered_models
    ]
    return jsonify(models)


@catch_mlflow_exception
def get_registered_model_users(name: str):
    if not get_is_admin():
        current_user = store.get_user(get_username())
        if not can_manage_registered_model(name, current_user.username):
            return make_forbidden_response()
    list_users = store.list_users(all=True)
    # Filter users who are associated with the given model
    users = []
    for user in list_users:
        # Check if the user is associated with the model
        user_models = {model.name: model.permission for model in user.registered_model_permissions} if user.registered_model_permissions else {}
        if name in user_models:
            users.append(
                {
                    "username": user.username,
                    "permission": user_models[name],
                    "kind": "user" if not user.is_service_account else "service-account",
                }
            )
    return jsonify(users)
