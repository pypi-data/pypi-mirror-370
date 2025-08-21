from lambda_happy.dependency_utils import check_dependencies

REQUIRED_DEPS = ["torch", "matplotlib", "numpy", "pandas"]
OPTIONAL_DEPS = ["PyQt5"]

PACKAGE_NAME = "lambda_happy"


GROUP_NAME = "validation"


def check_required_dependencies():
    return check_dependencies(
        REQUIRED_DEPS, required=True, group_name=GROUP_NAME, package_name=PACKAGE_NAME
    )


def check_optional_dependencies():
    return check_dependencies(
        OPTIONAL_DEPS, required=False, group_name=GROUP_NAME, package_name=PACKAGE_NAME
    )
