from experiment import *

# This function puts all the modules together to import and process the data
def main(save=True, operation=NEW, phase=ALL, inFile=INPUT_FILE, outPath=''):

  # new experiment
  if operation == NEW:
    experiment = Experiment(operation=operation,
                            inFile=inFile,
                            outPath=outPath,
                            verbose=DEBUG
                            )

  else:
    print(f'Error: Invalid operation: {operation}')
    print(f'Allowed operations are:')
    print(f'\t - {NEW} for running a new experiment')
    return False

  if not experiment.status:
    print(f'Error: Something wrong with the experiment initialization')
    return False

  if phase == ALL:
    if experiment.run():
      experiment.info()
  else:
    print(f'Error: Selected an invalid experiment phase: {phase}')
    print(f'Allowed phases are:')
    print(f'\t - {ALL} for running all phases of the experiment')
    return False

  return True

main()
