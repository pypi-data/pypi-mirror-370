CREATE_GITHUB_CONFIG_MUTATION: str = """
    mutation CreateGithubConfig(
        $githubPat: String!,
    ) {
        createGithubConfig(
            githubPat: $githubPat
        ) {
            __typename
            ... on GithubConfig {
                githubConfigUuid
                githubPat
            }
        }
    }
"""

CHECK_GITHUB_CONFIG_VALIDITY_QUERY: str = """
    query CheckGithubConfigValidity {
        checkGithubConfigValidity {
            __typename
            ... on GithubConfigValidityResult {
                isValid
                message
            }
            ... on Error {
                message
            }
        }
    }
"""

REPOS_FOR_GITHUB_CONFIG_QUERY: str = """
    query ReposForGithubConfig {
        reposForGithubConfig {
            __typename
            ... on GithubConfigRepos {
                repos {
                    id
                    name
                    fullName
                    private
                    owner
                    description
                }
                orgs {
                    login
                    id
                    url
                }
            }
            ... on Error {
                message
            }
        }
    }
"""
