Feature: Spotify Widget Integration
  As a runner
  I want a Spotify preview widget
  To hear snippets of my curated playlist

  Scenario: Spotify Widget reveal
    Given the Flask application is running
    When I submit a pace of "5:00" and genre "rock"
    Then I should see the Spotify widget container
    And the Spotify iframe should have a trackset URI
    And I should see the track list below the widget
