# Copyright (c) 2022 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import argparse
import json

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Sequence, Set

import qumulo.lib.opts
import qumulo.rest.s3 as s3

from qumulo.lib.identity_util import Identity
from qumulo.lib.request import pretty_json
from qumulo.lib.util import tabulate
from qumulo.rest_client import RestClient


class GetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_get_settings'
    SYNOPSIS = 'Retrieve S3 server settings'

    @staticmethod
    def main(rest_client: RestClient, _args: argparse.Namespace) -> None:
        print(rest_client.s3.get_settings().to_json(sort_keys=True, indent=4))


class ModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_modify_settings'
    SYNOPSIS = 'Modify S3 server settings'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--disable',
            '-d',
            dest='enabled',
            help='Disable S3 server',
            action='store_false',
            default=None,
        )
        enable_group.add_argument(
            '--enable',
            '-e',
            dest='enabled',
            help='Enable S3 server',
            action='store_true',
            default=None,
        )
        parser.add_argument(
            '--base-path',
            dest='base_path',
            help=(
                'The default bucket directory prefix for all S3 buckets created without an'
                ' explicitly specified path. You must specify this directory as an absolute path.'
            ),
            required=False,
        )
        parser.add_argument(
            '--multipart-upload-expiry-interval',
            dest='multipart_upload_expiry_interval',
            help=(
                'The time period during which the system permits a multipart upload to remain'
                ' unmodified. When this time period elapses, the system considers the multipart'
                ' upload stale and cleans it up automatically. Specify the time period in the'
                ' <quantity><units> format (for example, 5days). Quantity must be a positive'
                ' integer less than 100 and units must be one of the following: months, weeks,'
                ' days, or hours. To disable automatic multipart upload cleanup, specify never for'
                ' quantity and do not specify any units.'
            ),
            required=False,
            default=None,
        )
        secure_group = parser.add_mutually_exclusive_group()
        secure_group.add_argument(
            '--secure',
            dest='secure',
            help='Configure the S3 server to accept only HTTPS connections',
            action='store_true',
            default=None,
        )
        secure_group.add_argument(
            '--insecure',
            dest='secure',
            help='Configure the S3 server to accept both HTTP and HTTPS connections',
            action='store_false',
            default=None,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if (
            args.enabled is None
            and args.base_path is None
            and args.multipart_upload_expiry_interval is None
            and args.secure is None
        ):
            err_msg = (
                'You must use at least one of the following flags: [--disable, --enable,'
                ' --base-path, --multipart-upload-expiry-interval, --secure, --insecure]'
            )

            raise ValueError(err_msg)

        config = s3.ConfigPatch()

        if args.enabled is not None:
            config.enabled = args.enabled
        if args.base_path is not None:
            config.base_path = args.base_path
        if args.multipart_upload_expiry_interval is not None:
            config.multipart_upload_expiry_interval = args.multipart_upload_expiry_interval
        if args.secure is not None:
            config.secure = args.secure

        print(rest_client.s3.modify_settings(config).to_json(sort_keys=True, indent=4))


def make_access_keys_table(
    keys: Sequence[s3.AccessKeyDescription], display_headers: bool = True
) -> str:
    headers = ['access_key_id', 'owner', 'creation_time'] if display_headers else None
    rows = []
    for key in keys:
        row = []
        row.append(key.access_key_id)
        row.append(str(Identity(key.owner)))
        row.append(key.creation_time)
        rows.append(row)
    return tabulate(rows, headers)


class ListAccessKeysCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_list_access_keys'
    SYNOPSIS = 'List S3 access keys'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--json', action='store_true', help='Output JSON instead of table.')
        identity = parser.add_mutually_exclusive_group(required=False)
        identity.add_argument(
            '--user',
            type=Identity,
            help=(
                'Show access keys belonging to a specific user. Use an auth_id, SID, or name'
                ' optionally qualified with a domain prefix (e.g "local:name", "ad:name",'
                ' "AD\\name") or an ID type (e.g. "auth_id:513", "SID:S-1-1-0"). Groups are not'
                ' supported for access tokens, must be a user.'
            ),
        )
        identity.add_argument(
            '--self', action='store_true', help=('List only access keys that target yourself.')
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        def list_access_keys_tab(rest_client: RestClient, user: Optional[Identity]) -> None:
            results = rest_client.s3.list_access_keys(user=user)
            print(make_access_keys_table(results.entries, True))
            while results.paging.next:
                results = rest_client.s3.list_access_keys(user=user, start_at=results.paging.next)
                print(make_access_keys_table(results.entries, False))

        def list_access_keys_json(rest_client: RestClient, user: Optional[Identity]) -> None:
            def append_asdict(
                trg: List[Dict[str, Any]], src: Sequence[s3.AccessKeyDescription]
            ) -> None:
                for access_key in src:
                    trg.append(asdict(access_key))

            entries: List[Dict[str, Any]] = []
            response = rest_client.s3.list_access_keys(user=user)
            append_asdict(entries, response.entries)
            while response.paging.next is not None:
                response = rest_client.s3.list_access_keys(user=user, start_at=response.paging.next)
                append_asdict(entries, response.entries)

            print(pretty_json({'entries': entries}))

        user = args.user

        if args.self:
            user = Identity({'auth_id': rest_client.auth.who_am_i()['id']})

        if args.json:
            list_access_keys_json(rest_client, user)
        else:
            list_access_keys_tab(rest_client, user)


class CreateAccessKeyCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_create_access_key'
    SYNOPSIS = 'Create S3 access key'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        identity = parser.add_mutually_exclusive_group(required=True)
        identity.add_argument(
            'identifier',
            nargs='?',
            help=(
                'An auth_id, SID, or a name optionally qualified by a domain prefix (for example, '
                '"local:name", "ad:name", "AD\\name") or an ID type (for example, "auth_id:513", '
                '"SID:S-1-1-0"). Qumulo Core supports only users (not groups) for S3 access keys.'
            ),
        )
        identity.add_argument('--auth-id', type=int, help='The auth_id of the Qumulo Core user')
        identity.add_argument(
            '--self',
            action='store_true',
            help=('Create an s3 access key for the currently logged on user'),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        client = rest_client

        if args.auth_id:
            identity = Identity({'auth_id': str(args.auth_id)})
        elif args.self:
            identity = Identity({'auth_id': client.auth.who_am_i()['id']})
        else:
            identity = Identity(args.identifier)

        print(pretty_json(asdict(client.s3.create_access_key(identity))))


class DeleteAccessKeyCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_delete_access_key'
    SYNOPSIS = 'Delete an S3 access key'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--id', type=str, help='The identifier of the access key to delete.', required=True
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.s3.delete_access_key(args.id)


def make_buckets_table(buckets: Sequence[s3.BucketDescription]) -> str:
    headers = ['name', 'creation_time', 'path', 'versioning', 'locking']
    rows = []
    for bucket in buckets:
        row = []
        row.append(bucket.name)
        row.append(bucket.creation_time)
        row.append(bucket.path)
        row.append(bucket.versioning)
        row.append('Enabled' if bucket.lock_config.enabled else 'Disabled')
        rows.append(row)
    return tabulate(rows, headers)


class ListBucketsCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_list_buckets'
    SYNOPSIS = 'List all S3 buckets'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--json', action='store_true', help='List S3 buckets in JSON format (not in a table)'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        results = rest_client.s3.list_buckets()
        if args.json:
            buckets = asdict(results)
            for bucket in buckets['buckets']:
                bucket.pop('anonymous_access_enabled')  # DEPRECATED
            print(pretty_json(buckets))
        else:
            print(make_buckets_table(results.buckets))


class GetBucketCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_get_bucket'
    SYNOPSIS = 'Retrieve details for an S3 bucket'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--name', help='The name of the S3 bucket for which to retrieve details', required=True
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        results = rest_client.s3.list_buckets()
        for bucket in results.buckets:
            if bucket.name == args.name:
                bucket_dict = asdict(bucket)
                bucket_dict.pop('anonymous_access_enabled')  # DEPRECATED
                print(pretty_json(bucket_dict))
                return
        print(f'"{args.name}" not found.')


class CreateBucketCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_add_bucket'
    SYNOPSIS = 'Create an S3 bucket'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--name', help='The name of the bucket to create', required=True)
        parser.add_argument(
            '--fs-path',
            help=(
                'The absolute path to use as the bucket root directory. The user must have '
                'permission to read the directory.'
            ),
        )
        parser.add_argument(
            '--create-fs-path',
            help=(
                'Create the bucket root directory if it does not already exist.'
                ' The user must have permission to create the bucket root directory.'
            ),
            action='store_true',
        )
        parser.add_argument(
            '--enable-object-lock',
            help=('Create the bucket with versioning and object locking enabled.'),
            action='store_true',
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.fs_path is None and args.create_fs_path:
            err_msg = 'You can use the --create-fs-path flag only with the --fs-path flag.'
            raise ValueError(err_msg)

        results = rest_client.s3.create_bucket(
            name=args.name,
            path=args.fs_path,
            create_path=args.create_fs_path,
            object_lock_enabled=args.enable_object_lock,
        )
        bucket = asdict(results)
        bucket.pop('anonymous_access_enabled')  # DEPRECATED
        print(pretty_json(bucket))


class DeleteBucketCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_delete_bucket'
    SYNOPSIS = 'Delete an S3 bucket'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--name', help='The name of the S3 bucket to delete', required=True)
        parser.add_argument(
            '--delete-root-dir',
            action='store_true',
            help=(
                'If specified, the operation succeeds only if the bucket root directory is empty,'
                ' and the caller has the permissions for unlinking the bucket root directory from'
                ' the S3 bucket. By default, the directory to be deleted can contain objects.'
            ),
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.s3.delete_bucket(name=args.name, delete_root_dir=args.delete_root_dir)


class ModifyBucketCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_modify_bucket'
    SYNOPSIS = (
        'Modify the settings of the given bucket. Use this command to update the bucket versioning'
        ' state. Using this command to enable anonymous access to a bucket has been disabled, use'
        ' s3_set_bucket_policy instead.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--name', help='The name of the bucket to be modified', required=True)

        versioning_group = parser.add_mutually_exclusive_group()
        versioning_group.add_argument(
            '--suspend-versioning',
            dest='versioning',
            help='Suspends object versioning',
            action='store_const',
            const='Suspended',
            default=None,
        )
        versioning_group.add_argument(
            '--enable-versioning',
            dest='versioning',
            help='Enables object versioning',
            action='store_const',
            const='Enabled',
            default=None,
        )

        locking_group = parser.add_mutually_exclusive_group()
        locking_group.add_argument(
            '--enable-object-lock-without-retention',
            dest='locking',
            help='Enable Object Lock with no default retention period. (Requires versioning to be '
            'enabled for the specified S3 bucket.)',
            action='store_const',
            const='Enabled',
        )
        locking_group.add_argument(
            '--enable-object-lock-with-retention-days',
            dest='retention_days',
            help='Enable Object Lock with the retention period specified in days.',
            type=int,
        )
        locking_group.add_argument(
            '--enable-object-lock-with-retention-years',
            dest='retention_years',
            help='Enable Object Lock with the retention period specified in years.',
            type=int,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if (
            args.versioning is None
            and args.locking is None
            and args.retention_days is None
            and args.retention_years is None
        ):
            err_msg = (
                'Specify at least one of the following flags: [--enable-versioning, '
                '--suspend-versioning, --enable-object-lock-without-retention, '
                '--enable-object-lock-with-retention-days, '
                '--enable-object-lock-with-retention-years]'
            )
            raise ValueError(err_msg)

        patch = s3.BucketPatch()

        def patch_retention_period(units: str, value: int) -> None:
            if value == 0:
                raise ValueError('Enter a value greater than 0 for the default retention period.')
            patch.versioning = 'Enabled'
            patch.lock_config = s3.BucketLockConfiguration(
                enabled=True, default_retention=s3.BucketDefaultRetention(units=units, value=value)
            )

        if args.locking:
            patch.versioning = 'Enabled'
            patch.lock_config = s3.BucketLockConfiguration(enabled=True)
        elif args.retention_days is not None:
            patch_retention_period('days', args.retention_days)
        elif args.retention_years is not None:
            patch_retention_period('years', args.retention_years)

        if args.versioning:
            patch.versioning = args.versioning

        bucket = asdict(rest_client.s3.modify_bucket(name=args.name, patch=patch))
        bucket.pop('anonymous_access_enabled')  # DEPRECATED
        print(pretty_json(bucket))


class ListUploadsCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_list_uploads'
    SYNOPSIS = (
        'List S3 uploads in progress, including user-initiated multipart uploads and system-'
        'initiated uploads that the PutObject and CopyObject API actions use.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--bucket', help='The S3 bucket for which to list uploads', required=True
        )
        parser.add_argument(
            '--starts-with',
            help='List uploads only for keys that begin with the specified string',
            required=False,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        starts_with = args.starts_with

        def append_asdict(tgt: List[Dict[str, Any]], src: Sequence[s3.UploadDescription]) -> None:
            for upload in src:
                if starts_with and not upload.key.startswith(starts_with):
                    continue
                tgt.append(asdict(upload))

        uploads: List[Dict[str, Any]] = []

        response = rest_client.s3.list_uploads(bucket=args.bucket)
        append_asdict(uploads, response.uploads)
        while response.paging.next is not None:
            response = rest_client.s3.list_uploads(
                bucket=args.bucket, start_after=response.paging.next
            )
            append_asdict(uploads, response.uploads)

        print(pretty_json({'uploads': uploads}))


class AbortUploadCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_abort_upload'
    SYNOPSIS = (
        'Aborts an S3 upload in progress. You can perform this operation on user-initiated'
        ' multipart uploads and system-initiated uploads that the PutObject and CopyObject API'
        ' actions use.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--bucket', help='The S3 bucket to which the upload was initiated', required=True
        )
        parser.add_argument(
            '--upload-id', help='The identifier of the upload to abort.', required=True
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.s3.abort_upload(bucket=args.bucket, upload_id=args.upload_id)


class SetPolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_set_bucket_policy'
    SYNOPSIS = (
        'Upload the access policy JSON file that the --file flag specifies to the S3 bucket name'
        ' that the --bucket flag specifies.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--bucket',
            help='The name of the S3 bucket whose policy is to be configured',
            required=True,
        )
        parser.add_argument(
            '--file',
            help=(
                'The access policy file to upload. For an access policy template, use the '
                'qq s3_get_bucket_policy --example command. For what actions you are allowed use, '
                'run the qq s3_bucket_policy_explain_access admin command on the bucket.'
            ),
            required=True,
        )
        parser.add_argument(
            '--allow-remove-self',
            help=(
                'Allow the configured policy to remove the ability to modify itself from the'
                ' current user.'
            ),
            action='store_true',
            default=None,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        policy_string = ''
        with open(args.file) as f:
            policy_string = f.read()
        policy_json = json.loads(policy_string)
        policy = s3.Policy.from_dict(policy_json)
        rest_client.s3.put_bucket_policy(
            bucket=args.bucket, policy=policy, allow_remove_self=args.allow_remove_self
        )
        print('Upload complete')


def apply_statement_modifications(statement: s3.PolicyStatement, args: argparse.Namespace) -> None:
    if args.sid is not None:
        statement.sid = args.sid
    if args.type is not None:
        statement.effect = args.type
    if args.new_principals is not None:
        statement.principals = args.new_principals.split(',')
    if args.new_actions is not None:
        statement.action = args.new_actions.split(',')


class ModifyPolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_modify_bucket_policy'
    SYNOPSIS = 'Modify the access policy for --bucket.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--bucket',
            help='The name of the S3 bucket whose access policy is to be modified',
            required=True,
        )
        parser.add_argument(
            '--allow-remove-self',
            help='Allow the policy set to remove the ability for this user to change the policy.',
            action='store_true',
            default=None,
        )
        subparsers = parser.add_subparsers(dest='command')
        delete = subparsers.add_parser('delete_statement', help='Delete a policy statement.')
        delete.add_argument(
            '--index', help='The index of the statment to delete.', type=int, required=True
        )

        append = subparsers.add_parser(
            'append_statement',
            help='Append a policy statement granting full access to the `local:admin`.',
        )
        append.add_argument('--type', help='Specify Allow or Deny.', required=True)
        append.add_argument('--sid', help='Specify the optional SID string.', required=False)
        append.add_argument(
            '--principals',
            help='Use the provided comma separated list of principals.',
            required=True,
        )
        append.add_argument(
            '--actions', help='Use the provided comma separated list of actions.', required=True
        )

        modify = subparsers.add_parser('modify_statement', help='Modify a policy statement.')
        modify.add_argument(
            '--index', help='The index of the statment to modify.', type=int, required=True
        )
        modify.add_argument(
            '--new-principals',
            help='Set the provided comma separated list of principals.',
            required=False,
        )
        modify.add_argument(
            '--new-actions',
            help='Set the provided comma separated list of actions.',
            required=False,
        )
        modify.add_argument('--type', help='Specify Allow or Deny.', required=False)
        modify.add_argument('--sid', help='Specify the optional SID string.', required=False)

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        policy = rest_client.s3.get_bucket_policy(bucket=args.bucket)
        if policy is None:
            policy = s3.Policy(id='Default', version=s3.POLICY_VERSION_2012, statements=[])

        if args.command == 'append_statement':
            principals = args.principals.split(',')
            action = args.actions.split(',')
            statement = s3.PolicyStatement(
                effect=args.type, sid=args.sid, principals=principals, action=action
            )
            policy.statements.append(statement)

        elif args.command == 'delete_statement':
            count = len(policy.statements)
            if args.index == 0 or count < args.index:
                raise ValueError(f'Index {args.index} not found in policy of length {count}.')
            policy.statements = [
                s for (i, s) in enumerate(policy.statements) if i + 1 != args.index
            ]

        elif args.command == 'modify_statement':
            count = len(policy.statements)
            if args.index == 0 or count < args.index:
                raise ValueError(f'Index {args.index} not found in policy of length {count}.')
            apply_statement_modifications(policy.statements[args.index - 1], args)

        else:
            raise ValueError(
                'One of append_statement, delete_statement, or modify_statement must be provided.'
            )

        print('Uploading The Following Policy:')
        print('===============================\n')
        print(pretty_json(policy.to_dict()))

        rest_client.s3.put_bucket_policy(
            bucket=args.bucket, policy=policy, allow_remove_self=args.allow_remove_self
        )


class GetPolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_get_bucket_policy'
    SYNOPSIS = 'Retrieve entries of the access policy json stored at `BUCKET`.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--bucket',
            help='The target bucket for which the access policy will be retrieved',
            required=False,
        )
        parser.add_argument(
            '--example', help='Print an example Policy.', required=False, action='store_true'
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        if args.example:
            if args.bucket is not None:
                raise ValueError('Bucket name is not allowed with --example.')

            statement1 = s3.PolicyStatement(
                effect='Allow',
                sid='EveryoneGet',
                principals=['Everyone'],
                action=[
                    's3:GetBucketPolicy',
                    's3:GetBucketAcl',
                    's3:GetBucketLocation',
                    's3:GetBucketNotification',
                    's3:GetBucketObjectLockConfiguration',
                    's3:GetBucketReplication',
                    's3:GetBucketVersioning',
                    's3:GetEncryptionConfiguration',
                    's3:GetLifecycleConfiguration',
                    's3:GetObject',
                    's3:GetObjectAcl',
                    's3:GetObjectAttributes',
                    's3:GetObjectRetention',
                    's3:GetObjectTagging',
                    's3:GetObjectVersion',
                    's3:ListBucket',
                    's3:ListBucketMultipartUploads',
                    's3:ListMultipartUploadParts',
                ],
            )
            statement2 = s3.PolicyStatement(
                effect='Allow',
                sid='AuthenticatedPut',
                principals=['Authenticated Users'],
                action=[
                    's3:AbortMultipartUpload',
                    's3:DeleteBucket',
                    's3:DeleteObject',
                    's3:DeleteObjectTagging',
                    's3:DeleteObjectVersion',
                    's3:PutObject',
                    's3:PutObjectRetention',
                    's3:PutObjectTagging',
                ],
            )
            statement3 = s3.PolicyStatement(
                effect='Allow',
                sid='AdminModifyPolicy',
                principals=['local:Admin'],
                action=[
                    's3:DeleteBucketPolicy',
                    's3:PutBucketObjectLockConfiguration',
                    's3:PutBucketPolicy',
                    's3:PutBucketVersioning',
                    's3:*',
                ],
            )
            example_policy = s3.Policy(
                id='DefaultPolicy',
                version=s3.POLICY_VERSION_2012,
                statements=[statement1, statement2, statement3],
            )
            pretty_policy = pretty_json(example_policy.to_dict())
            print(pretty_policy)
        else:
            if args.bucket is None:
                raise ValueError('A bucket name must be specified.')

            policy = rest_client.s3.get_bucket_policy(args.bucket)
            if policy is None:
                print('{}')
            else:
                pretty_str = pretty_json(policy.to_dict())
                print(pretty_str)


class DeletePolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_delete_bucket_policy'
    SYNOPSIS = 'Remove the access policy stored at `BUCKET`.'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--bucket',
            help='The target bucket for which the access policy will be removed.',
            required=True,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        rest_client.s3.delete_bucket_policy(args.bucket)


def list_actions_in_table(explanation: s3.PolicyAccessExplanation) -> str:
    rbac_actions = set(explanation.rbac_allowed_actions)
    policy_actions: Set[str] = set()
    for access in explanation.statement_access:
        if access and access.allow:
            policy_actions.update(access.actions)

    headers = ['action', 'source']
    rows = []
    for action in explanation.allowed_actions:
        row = []
        row.append(action)
        source = []
        if action in rbac_actions:
            source.append('RBAC')
        if action in policy_actions or 's3:*' in policy_actions:
            source.append('policy')
        if not source:
            source.append('empty-policy')
        row.append(', '.join(source))
        rows.append(row)

    return tabulate(rows, headers)


class PolicyExplainAccessCommand(qumulo.lib.opts.Subcommand):
    NAME = 's3_bucket_policy_explain_access'
    SYNOPSIS = 'Details a users access as allowed by the bucket policy'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--bucket',
            help='The bucket for which the access policy will be explained.',
            required=True,
        )
        identity = parser.add_mutually_exclusive_group(required=True)
        identity.add_argument(
            'identifier',
            nargs='?',
            help=(
                'An auth_id, SID, or name optionally qualified with a domain prefix (e.g '
                '"local:name", "ad:name", "AD\\name") or an ID type (e.g. "auth_id:513", '
                '"SID:S-1-1-0"). Groups are not supported for access keys, must be a user.'
            ),
        )
        identity.add_argument('--auth-id', type=int, help='Auth ID of the qumulo user')
        identity.add_argument(
            '--anonymous',
            dest='anonymous',
            help='An unauthenticated S3 user',
            action='store_true',
            default=None,
        )

    @staticmethod
    def main(rest_client: RestClient, args: argparse.Namespace) -> None:
        identity = None
        if args.auth_id:
            identity = Identity({'auth_id': str(args.auth_id)})
        elif args.identifier:
            identity = Identity(args.identifier)

        result = rest_client.s3.bucket_policy_explain_access(bucket=args.bucket, identity=identity)

        if identity:
            print(f'Bucket `{args.bucket}` access for identity:')
            print(pretty_json(result.identity))
        else:
            print(f'Bucket `{args.bucket}` access for anonymous users:')

        if len(result.statement_access) > 0:
            print('\nPolicy statements access evaluation:')
            for i, access in enumerate(result.statement_access, start=1):
                print(f'==== {i} ====')
                if access:
                    effect = 'Allow' if access.allow else 'Deny'
                    print(f'\tEffect: {effect}')
                    actions = ', '.join(access.actions)
                    print(f'\tActions: {actions}')
                else:
                    print('\tEffect: None')
        else:
            print('\nNo bucket policy defined for bucket.')

        if len(result.rbac_allowed_actions) > 0:
            print('\nS3 actions granted by RBAC:')
            print(', '.join(result.rbac_allowed_actions))
        else:
            print('\nNo S3 actions granted by RBAC.')

        if len(result.allowed_actions) > 0:
            print('\nS3 actions allowed for bucket:')
            print(list_actions_in_table(result))
        else:
            print('\nNo S3 actions allowed by policy.')
