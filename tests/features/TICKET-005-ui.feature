Feature: Web Interface
  As a runner
  I want to use a web interface
  To generate my running playlists easily

  Scenario: Generate a playlist from the home page
    Given the Flask application is running
    When I submit a pace of "5:30" and genre "rock"
    Then I should see a list of recommended tracks
    And the BPM range should be calculated correctly
