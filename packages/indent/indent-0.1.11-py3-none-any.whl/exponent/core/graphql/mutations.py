HALT_CHAT_STREAM_MUTATION: str = """
  mutation HaltChatStream($chatUuid: UUID!) {
    haltChatStream(chatUuid: $chatUuid) {
      __typename
    }
  }
"""


SET_LOGIN_COMPLETE_MUTATION: str = """
  mutation SetLoginComplete {
    setLoginComplete {
      __typename
      ... on User {
        userApiKey
      }
      ... on UnauthenticatedError {
        message
      }
    }
  }
"""


REFRESH_API_KEY_MUTATION = """
mutation RefreshApiKey {
    refreshApiKey {
        ... on User {
            userApiKey
        }
        ... on UnauthenticatedError {
            message
        }
    }
}
"""

START_CHAT_TURN_MUTATION = """
mutation StartChatTurnMutation($chatInput: ChatInput!, $parentUuid: String, $chatConfig: ChatConfig!) {
    startChatReply(
        chatInput: $chatInput,
        parentUuid: $parentUuid,
        chatConfig: $chatConfig
    ) {
      __typename
      ... on UnauthenticatedError {
          message
      }
      ... on ChatNotFoundError {
          message
      }
      ... on Chat {
          chatUuid
      }
  }
}
"""


CREATE_CLOUD_CHAT_MUTATION = """
mutation CreateCloudChat($configId: String!) {
  createCloudChat(cloudConfigUuid: $configId) {
    __typename
    ...on Chat {
      chatUuid
    }
    ...on CloudSessionError {
      message
    }
    ...on UnauthenticatedError {
      message
    }
  }
}
"""
