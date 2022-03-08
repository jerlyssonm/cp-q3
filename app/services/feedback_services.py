from werkzeug.exceptions import BadRequest


obj = {"text": "é noiz cachorro","rating": "2"}

def validate_feedback(request_data: dict):
    valid_keys = set(["text", "rating"])
    allowed_number_of_keys_ = 2

    if len(request_data) < allowed_number_of_keys_:
        missing_keys = valid_keys - set(request_data.keys())
        error_description = {"missing keys": list(missing_keys)}
    
        if len(missing_keys) == 1:
            error_description = {"missing key": list(missing_keys)[0]}
        
        raise BadRequest(description=error_description)

    wrong_keys = set(request_data) - valid_keys

    if wrong_keys:
        error_description = {"wrong key": list(wrong_keys)}

        if len(wrong_keys) == 1:
            error_description = {"wrong key": list(wrong_keys)}

        raise BadRequest(description=error_description)
    formatted_feedback = {
        "text": request_data["text"].capitalize(),
        "rating": float(request_data["rating"])
    }
    return formatted_feedback
