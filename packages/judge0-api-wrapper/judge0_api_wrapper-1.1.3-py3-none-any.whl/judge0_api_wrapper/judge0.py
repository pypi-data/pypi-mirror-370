import time
import base64

import requests
from furl import furl

from .exceptions import LanguageNotFound
from .schemas import Submission, SubmissionResult, CreateSubmission
from .custom_types import Status

class Judge0:
    def __init__(
        self, 
        Judge0_ip: str, 
        X_Auth_Token: str, 
        X_Auth_User: str
    ):
        ''' Init

        Parameters
        ----------
        Judgeo_ip : str
            IP address with port of the Judge0 server
        X_Auth_Token : str
            X-Auth token
        X_Auth_User : str
            X-Auth user
        '''
        self.__judge0_ip = furl(Judge0_ip)
        self.__session: requests.Session = requests.session()
        self.__session.headers['X-Auth-Token'] = X_Auth_Token
        self.__session.headers['X-Auth-User'] = X_Auth_User
        self.__check_tokens()
        self.__init_languages_dict()

    def __check_tokens(
        self
    ):
        ''' Check if the given tokens are valid. If invalid, it raises a requests.HTTPError exception; otherwise, it returns None. 
        '''
        authn_response = self.__session.post(self.__judge0_ip / 'authenticate')
        authn_response.raise_for_status()
        authz_reponse = self.__session.post(self.__judge0_ip / 'authorize')
        authz_reponse.raise_for_status()

    def __init_languages_dict(
        self
    ):
        ''' Initialises all supported languages
        '''
        languages_list = self.__session.get(self.__judge0_ip / 'languages').json()
        self.__languages: dict[int, str] = {item['id']: item['name'] for item in languages_list}

    def __base64_encode(
        self, 
        create_submission: CreateSubmission
    ) -> CreateSubmission:
        ''' Encodes all string fields in submission with base64
        '''
        new_submission = create_submission.model_copy()
        new_submission.source_code = base64.b64encode(create_submission.source_code.encode()).decode()
        if create_submission.stdin:
            new_submission.stdin = base64.b64encode(create_submission.stdin.encode()).decode()
        if create_submission.expected_output:
            new_submission.expected_output = base64.b64encode(create_submission.expected_output.encode()).decode()
        return new_submission

    @property
    def languages(
        self
    ) -> dict[int, str]:
        '''Returns a dict of available languages

        Returns
        -------
            A dictionary that contatins all supported languages
        '''
        return self.__languages

    def submit(
        self, 
        create_submission: CreateSubmission, 
        encode_in_base64: bool = True
    ) -> Submission:
        '''Creates new submission

        Parameters
        ----------
        submission : CreateSubmission
            A submission to create. All str type fields must be plain
        encode_in_base64 : bool
            Whether to encode submission in base64

        Returns
        -------
        Submission
            Created submission

        Raises
        ------
        LanguageNotFound
        '''
        if self.languages.get(create_submission.language_id) is None:
            raise LanguageNotFound('Unknown language id. Use languages property to get a dict of available languages')
        
        if encode_in_base64:
            create_submission = self.__base64_encode(create_submission)

        data = create_submission.model_dump(exclude_none=True, exclude='date')

        response = self.__session.post(
            self.__judge0_ip / 'submissions', 
            json=data, 
            params={'base64_encoded': 'true' if encode_in_base64 else 'false'}
        )
        response.raise_for_status()

        token: str = response.json().get('token')
        submission = Submission(
            **data, token=token
        )
        return submission
    
    def submit_batch(
        self, 
        batch: list[CreateSubmission],
        encode_in_base64: bool = True
    ) -> list[Submission]:
        '''Creates new submissions

        Parameters
        ----------
        batch : list[CreateSubmission]
            Submissions to create. All str type fields must be plain
        encode_in_base64 : bool
            Whether to encode submissions in base64

        Returns
        -------
        list[Submission]
            Tokens for the created submissions

        Raises
        ------
        LanguageNotFound
        '''
        for create_submission in batch:
            if self.languages.get(create_submission.language_id) is None:
                raise LanguageNotFound('Unknown language id. Use languages property to get a dict of available languages')
        
        if encode_in_base64:
            batch = [self.__base64_encode(create_submission) for create_submission in batch]

        batch_data = [create_submission.model_dump(exclude_none=True, exclude='date') for create_submission in batch]

        response = self.__session.post(
            self.__judge0_ip / 'submissions/batch',
            json={'submissions': batch_data},
            params={'base64_encoded': 'true' if encode_in_base64 else 'false'}
        )
        response.raise_for_status()

        tokens = [item['token'] for item in response.json()]
        submissions = [Submission(
            **data, token=token
        ) for data, token in zip(batch_data, tokens)]
        return submissions

    def __get_info(
        self, 
        token: str
    ):
        '''Returns reponse body of the GET /submissions/{token} request
        '''
        response = self.__session.get(self.__judge0_ip / 'submissions' / token)
        response.raise_for_status()
        return response.json()
    
    def get_status(
        self, 
        submission: Submission
    ) -> Status:
        '''Returns current status of a sumbmission
        '''
        body: dict = self.__get_info(submission.token)
        return Status(body.get('status').get('id'))
    
    def get_statuses(
        self,
        submissions: list[Submission]
    ) -> list[Status]:
        ''' Docstring to write
        '''
        return [self.get_status(submission) for submission in submissions]
    
    def get_result(
        self,
        submission: Submission
    ) -> SubmissionResult:
        ''' Returns submission result
        '''
        status = self.get_status(submission)
        info: dict = self.__get_info(submission.token)
        return SubmissionResult(
            source_code=submission.source_code,
            language_id=submission.language_id,
            result=status,
            stdout='' if info.get('stdout') is None else info.get('stdout'),
            time=info.get('time'),
            memory=info.get('memory'),
            date=submission.date
        )
    
    def get_results(
        self,
        submissions: list[Submission]
    ) -> list[SubmissionResult]:
        ''' Returns submissions result
        '''
        return [self.get_result(submission) for submission in submissions]

    def wait_for_completion(
        self, 
        submission: Submission, 
        poll_interval: int = 1
    ) -> SubmissionResult:
        ''' Waits for a submission to complete and returns its result
        '''
        while 1:
            status = self.get_status(submission)
            if status in [Status.IN_QUEUE, Status.PROCESSING]:
                time.sleep(poll_interval)
                continue
            info: dict = self.__get_info(submission.token)
            return SubmissionResult(
                source_code=submission.source_code,
                language_id=submission.language_id,
                result=status,
                stdout=info.get('stdout'),
                time=info.get('time'),
                memory=info.get('memory'),
                date=submission.date
            )
        
    def wait_for_completions(
        self,
        submissions: list[Submission],
        poll_interval: int = 1
    ) -> list[SubmissionResult]:
        ''' Docstring to write
        '''
        submission_results = []
        for submission in submissions:
            submission_results.append(self.wait_for_completion(submission, poll_interval))
        return submission_results
