import subprocess

# Mozart Silent Exe 설치 경로
mozart_silent_path = r"C:\Program Files (x86)\VMS\Mozart\v2\Client\Bin\MozartSilent.exe"


def RunMozartSilent(on_exit, model_path, exp=None, noLinkedModel=False, arg=None):
    """
    Runs the given model path using subprocess.Popen and calls the function on_exit
    after the subprocess completes.
    on_exit is a callable object, model_path is the path to the model directory.
    """

    command = [mozart_silent_path] + [f"{model_path}"]

    if exp is not None:
        command.append(f'-exp:"{exp}"')

    if noLinkedModel:
        command.append('-noLinkedModel')

    if arg is not None:
        command.append(f'-arg:"{arg}"')

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in process.stdout:
        print(line.strip())

    process.wait()
    on_exit(model_path)  # The parameter of this can be changed in correspondence to what the user wants to implement


def function_to_call_on_exit(model_path):
    """
    Example use of on_exit function that is to be run after running the model.
    """
    # Do something when the subprocess exits
    print(f"Subprocess for model {model_path} has exited")


if __name__ == '__main__':
    model_path = r"C:\Users\vms\Desktop\silentsamplemodel\silent_sample_model1\model\MyModel.vmodel"
    experiment = "Experiment 1"
    noLinkedModel = False
    arg = r"C:\Model\args1.txt"

    RunMozartSilent(function_to_call_on_exit, model_path, exp=experiment, noLinkedModel=noLinkedModel, arg=arg)

