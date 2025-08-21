from moveshelf_api.api import Metadata

def getPatientMetadata(api, mySubjectId):
    """
    Retrieve and evaluate metadata for a patient.

    Args:
        api: The API client instance to interact with the server.
        mySubjectId (str): The ID of the patient.

    Returns:
        dict: The evaluated patient metadata.
    """
    subjectDetails = api.getSubjectDetails(mySubjectId)
    patientMetadata = eval(subjectDetails['metadata'])
    return patientMetadata


def getConditionsFromSession(session, conditions=[]):
    """
    Extract conditions and associated clips from a session.

    Args:
        session (dict): A dictionary containing session details, including `projectPath`, and `clips`.
        conditions (list, optional): A list to append or match conditions. Defaults to an empty list.

    Returns:
        list: A list of conditions, each containing `path`, `fullPath`, and `clips`.
    """
    sessionPath = session['projectPath']
    clips = session['clips']

    # Process clips to extract conditions
    for c in clips:
        clipPath = c['projectPath'].split(sessionPath)
        if len(clipPath) > 0 and len(clipPath[1]) > 0:
            conditionPath = clipPath[1]
            conditionFound = False
            for condition in conditions:
                if condition['path'] == conditionPath:
                    condition['clips'].append(c)
                    conditionFound = True
                    break

            if not conditionFound:
                condition = dict.fromkeys(['path', 'fullPath', 'clips'])
                condition['path'] = conditionPath
                condition['fullPath'] = sessionPath + conditionPath
                condition['clips'] = [c]
                conditions.append(condition)

    return conditions


def addOrGetTrial(api, session, condition, trialName=None):
    """
    Add a new trial or retrieve an existing one based on its name.

    Args:
        api: The API client instance to interact with the server.
        session (dict): A dictionary containing session details, including `projectPath` and `project`.
        condition (dict): The condition to associate the trial with, containing `path` and `clips`.
        trialName (str, optional): The name of the trial. If not provided, it will be auto-generated. Defaults to None.

    Returns:
        str: The ID of the trial clip.
    """
    trialCount = len(condition['clips'])

    if trialName is None:
        # Auto-generate trial name
        trialNumbers = [int(clip['title'].split('-')[1]) for clip in condition['clips'] if trialCount > 0]
        trialNumber = max(trialNumbers) if len(trialNumbers) > 0 else trialCount
        trialName = "Trial-" + str(trialNumber + 1)

    trialNames = [clip['title'] for clip in condition['clips'] if trialCount > 0]
    if trialName in trialNames:
        # Return existing clip ID
        iClip = trialNames.index(trialName)
        clipId = condition['clips'][iClip]['id']
    else:
        # Create a new clip
        metadata = Metadata()
        metadata['title'] = trialName
        metadata['projectPath'] = session['projectPath'] + condition['path']
        clipId = api.createClip(session['project']['name'], metadata)

    return clipId
