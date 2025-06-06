describe('test flow', () => {
  it('student flow', () => {
    // opens app
    cy.visit('http://localhost:8501');
    cy.wait(2000);
    cy.contains('Login Page');

    // can login as a student
    cy.contains('Continue as Student').click();
    cy.wait(2000);
    cy.contains('Upload Dental image');

    //continues without uploading image
    cy.contains('Next page').click();
    cy.wait(2000);
    cy.contains('Welcome to the manual page!');
    cy.contains('No image has been uploaded yet.').should('be.visible');

    // go back to upload image
    cy.contains('Upload image').click();
    cy.wait(3000);
    cy.contains('Upload Dental image');

    // upload image
    cy.get('input[type="file"]')
      .selectFile('cypress/fixtures/case_1.jpeg', { force: true });
    cy.wait(1000);
    cy.contains("File 'case_1' is uploaded successfully", { timeout: 10000 })
      .should('be.visible');

    // go to next page
    cy.contains('Next page').click();
    cy.wait(2000);
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

  it('professional flow', () => {
    // opens app
    cy.visit('http://localhost:8501');
    cy.wait(2000);
    cy.contains('Login Page');

    // can login as a professional
    cy.get('input[type="text"]').first().type('sarah');
    cy.get('input[type="password"]').type('password');
    cy.get('button').contains('Login').last().click();
    cy.wait(3000);
    cy.contains('Upload Dental image');
    cy.contains('Menu').should('be.visible');

    // upload image
    cy.get('input[type="file"]')
      .selectFile('cypress/fixtures/case_1.jpeg', { force: true });
    cy.wait(1000);
    cy.contains("File 'case_1' is uploaded successfully", { timeout: 10000 })
      .should('be.visible');

    // go to next page
    cy.contains('Next page').click();
    cy.wait(2000);
    cy.contains('Welcome to the manual page!');

    // click teeth
    cy.contains('16').click();
    cy.wait(2000);
    cy.contains('Tooth 16').should('be.visible');
    cy.contains('Present').click();
    cy.wait(1000);
    cy.contains("Dental filling").click();
    cy.wait(1000);
    cy.contains("Submit").click();

    // go to next page
    cy.contains('Next page').click();
    cy.wait(1000);
    cy.contains('Comparison page!');

    // click teeth
    cy.contains('47').click();
    cy.wait(1000);
    cy.contains("Save").click();
  });
});