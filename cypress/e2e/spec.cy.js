describe('test student flow', () => {
  it('Loads the app and checks for a title', () => {
    // opens app
    cy.visit('http://localhost:8501');
    cy.wait(1000);
    cy.contains('Login Page');

    // can login as a student
    cy.contains('Continue as Student').click();
    cy.wait(1000);
    cy.contains('Upload Dental image');

    //continues without uploading image
    cy.contains('Next page').click();
    cy.wait(1000);
    cy.contains('Welcome to the manual page!');
    cy.contains('No image has been uploaded yet.');

    // go back to upload image
    cy.contains('Upload image').click();
    cy.wait(1000);
    cy.contains('Upload Dental image');

    // upload image
    cy.get('input[type="file"]')
      .selectFile('cypress/fixtures/case_1.jpeg', { force: true });
    cy.wait(1000);
    cy.contains("File 'case_1' is uploaded successfully", { timeout: 10000 })
      .should('be.visible');

    // go to next page
    cy.contains('Next page').click();
    cy.wait(1000);
    cy.contains('Welcome to the manual page!');

    // click teeth
    cy.contains('16').click();
    cy.wait(1000);
    cy.contains('Tooth 16');
    cy.contains('Present').click();
    cy.wait(1000);
    cy.contains("Dental filling").click();
    cy.wait(1000);
    cy.contains("Submit").click();

    // go to next page
    cy.contains('Next page').click();
    cy.wait(1000);
    cy.contains('Welcome to the AI page!');

    // click teeth
    cy.contains('21').click();
    cy.wait(1000);
    cy.contains('Tooth 21');
    cy.contains('Missing').click();
    cy.wait(1000);
    cy.contains("Implant");
    cy.contains("Submit").click();

    // go to next page
    cy.contains('Next page').click();
    cy.wait(1000);
    cy.contains('Comparison page!');

  });
});