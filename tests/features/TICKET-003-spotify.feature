Feature: Spotify Integration
  Retrieve songs matching genres and tempo boundaries

  Scenario: Token retrieval on missing credentials
    Given missing Spotify credentials
    When I retrieve the token
    Then it raises a ValueError

  Scenario: Health check returns true on success
    Given a mock Spotify API with a valid token
    When I perform a health check
    Then the result should be true

  Scenario: Fetch recommendations successfully
    Given a mock Spotify API with a valid token
    And a genre "rock" with limits 150 to 160 BPM
    When I get recommendations
    Then I get a list of 2 tracks matching my criteria
