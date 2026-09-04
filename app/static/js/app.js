document.addEventListener("DOMContentLoaded", () => {
    const postCards = Array.from(
        document.querySelectorAll(".post-card")
    );

    const searchInput = document.getElementById(
        "post-search"
    );

    const statusFilter = document.getElementById(
        "status-filter"
    );

    const emptyState = document.getElementById(
        "empty-state"
    );

    const responseCountElement = document.getElementById(
        "response-count"
    );

    const postedCountElement = document.getElementById(
        "posted-count"
    );


    function showMessage(
        postId,
        message,
        type = "info"
    ) {
        const element = document.getElementById(
            `action-message-${postId}`
        );

        if (!element) {
            return;
        }

        element.textContent = message;

        element.classList.remove(
            "message-success",
            "message-error",
            "message-info"
        );

        element.classList.add(
            `message-${type}`
        );
    }


    function clearMessage(postId) {
        const element = document.getElementById(
            `action-message-${postId}`
        );

        if (!element) {
            return;
        }

        element.textContent = "";

        element.classList.remove(
            "message-success",
            "message-error",
            "message-info"
        );
    }


    function setButtonLoading(
        button,
        isLoading,
        loadingText = "Working..."
    ) {
        if (!button) {
            return;
        }

        if (isLoading) {
            button.dataset.previousText =
                button.textContent.trim();

            button.disabled = true;
            button.textContent = loadingText;

            button.classList.add(
                "button-loading"
            );

            return;
        }

        button.classList.remove(
            "button-loading"
        );
    }


    function getPostElements(postId) {
        return {
            card: document.getElementById(
                `post-card-${postId}`
            ),

            responseBox: document.getElementById(
                `response-box-${postId}`
            ),

            responseStatus: document.getElementById(
                `response-status-${postId}`
            ),

            generateButton: document.querySelector(
                `.generate-button[data-post-id="${postId}"]`
            ),

            copyButton: document.querySelector(
                `.copy-button[data-post-id="${postId}"]`
            ),

            linkedinButton: document.querySelector(
                `.linkedin-button[data-post-id="${postId}"]`
            ),

            postedButton: document.querySelector(
                `.posted-button[data-post-id="${postId}"]`
            ),
        };
    }


    function updateStatusBadge(
        element,
        status
    ) {
        if (!element) {
            return;
        }

        element.classList.remove(
            "status-empty",
            "status-draft",
            "status-posted"
        );

        if (status === "posted") {
            element.textContent = "posted";

            element.classList.add(
                "status-posted"
            );

            return;
        }

        if (status === "draft") {
            element.textContent = "draft";

            element.classList.add(
                "status-draft"
            );

            return;
        }

        element.textContent =
            "Not generated";

        element.classList.add(
            "status-empty"
        );
    }


    function incrementCounter(
        element,
        amount = 1
    ) {
        if (!element) {
            return;
        }

        const currentValue = Number(
            element.textContent.trim()
        );

        if (Number.isNaN(currentValue)) {
            return;
        }

        element.textContent =
            currentValue + amount;
    }


    function updateCardAfterGeneration(
        postId,
        generatedResponse
    ) {
        const {
            card,
            responseBox,
            responseStatus,
            generateButton,
            copyButton,
            linkedinButton,
            postedButton,
        } = getPostElements(postId);

        if (!card || !responseBox) {
            return;
        }

        responseBox.textContent =
            generatedResponse.response_text;

        responseBox.classList.remove(
            "response-box-empty"
        );

        updateStatusBadge(
            responseStatus,
            "draft"
        );

        card.dataset.status =
            "draft";

        if (generateButton) {
            generateButton.textContent =
                "Regenerate Response";

            generateButton.disabled =
                false;
        }

        if (copyButton) {
            copyButton.disabled =
                false;
        }

        if (linkedinButton) {
            linkedinButton.disabled =
                false;
        }

        if (postedButton) {
            postedButton.disabled =
                false;

            postedButton.textContent =
                "Mark Posted";

            postedButton.dataset.responseId =
                generatedResponse.id;

            postedButton.dataset.posted =
                "false";
        }

        incrementCounter(
            responseCountElement,
            1
        );

        applyFilters();
    }


    async function generateResponse(
        postId,
        button
    ) {
        clearMessage(postId);

        setButtonLoading(
            button,
            true,
            "Generating..."
        );

        try {
            const response = await fetch(
                `/api/posts/${postId}/generate-response`,
                {
                    method: "POST",
                    headers: {
                        "Accept":
                            "application/json",
                    },
                }
            );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "Unable to generate response."
                );
            }

            updateCardAfterGeneration(
                postId,
                data
            );

            showMessage(
                postId,
                "Sapho Bio response generated successfully.",
                "success"
            );
        } catch (error) {
            console.error(error);

            button.disabled =
                false;

            button.textContent =
                button.dataset.previousText ||
                "Generate Response";

            showMessage(
                postId,
                error.message ||
                    "Something went wrong while generating the response.",
                "error"
            );
        } finally {
            setButtonLoading(
                button,
                false
            );
        }
    }


    async function copyText(text) {
        if (
            navigator.clipboard &&
            window.isSecureContext
        ) {
            await navigator.clipboard.writeText(
                text
            );

            return;
        }

        const textArea =
            document.createElement(
                "textarea"
            );

        textArea.value = text;

        textArea.style.position =
            "fixed";

        textArea.style.opacity =
            "0";

        document.body.appendChild(
            textArea
        );

        textArea.focus();
        textArea.select();

        const copied =
            document.execCommand(
                "copy"
            );

        textArea.remove();

        if (!copied) {
            throw new Error(
                "Clipboard copy failed."
            );
        }
    }


    function getResponseText(postId) {
        const responseBox =
            document.getElementById(
                `response-box-${postId}`
            );

        if (!responseBox) {
            return "";
        }

        return responseBox
            .textContent
            .trim();
    }


    async function handleCopy(postId) {
        clearMessage(postId);

        const text =
            getResponseText(postId);

        if (!text) {
            showMessage(
                postId,
                "Generate a response first.",
                "error"
            );

            return;
        }

        try {
            await copyText(text);

            showMessage(
                postId,
                "Response copied to clipboard.",
                "success"
            );
        } catch (error) {
            console.error(error);

            showMessage(
                postId,
                "Unable to copy the response.",
                "error"
            );
        }
    }


    async function handleCopyAndOpen(
        postId,
        postUrl
    ) {
        clearMessage(postId);

        const text =
            getResponseText(postId);

        if (!text) {
            showMessage(
                postId,
                "Generate a response first.",
                "error"
            );

            return;
        }

        /*
         * Open the LinkedIn tab immediately while
         * the browser still considers this a direct
         * user interaction. This reduces the chance
         * that popup blockers interfere.
         */
        const linkedinWindow = window.open(
            postUrl,
            "_blank",
            "noopener,noreferrer"
        );

        try {
            await copyText(text);

            if (linkedinWindow) {
                showMessage(
                    postId,
                    "Response copied. LinkedIn opened in a new tab.",
                    "success"
                );
            } else {
                showMessage(
                    postId,
                    "Response copied. Your browser blocked the LinkedIn tab.",
                    "info"
                );
            }
        } catch (error) {
            console.error(error);

            showMessage(
                postId,
                "LinkedIn opened, but the response could not be copied.",
                "error"
            );
        }
    }


    async function markPosted(
        postId,
        button
    ) {
        clearMessage(postId);

        const responseId =
            button.dataset.responseId;

        if (!responseId) {
            showMessage(
                postId,
                "Generate a response first.",
                "error"
            );

            return;
        }

        if (
            button.dataset.posted ===
            "true"
        ) {
            return;
        }

        setButtonLoading(
            button,
            true,
            "Saving..."
        );

        try {
            const response = await fetch(
                `/api/responses/${responseId}/mark-posted`,
                {
                    method: "POST",
                    headers: {
                        "Accept":
                            "application/json",
                    },
                }
            );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "Unable to log response."
                );
            }

            const {
                card,
                responseStatus,
                postedButton,
            } = getPostElements(postId);

            if (card) {
                card.dataset.status =
                    "posted";
            }

            updateStatusBadge(
                responseStatus,
                "posted"
            );

            if (postedButton) {
                postedButton.textContent =
                    "Posted ✓";

                postedButton.disabled =
                    true;

                postedButton.dataset.posted =
                    "true";
            }

            incrementCounter(
                postedCountElement,
                1
            );

            showMessage(
                postId,
                "Engagement logged as posted.",
                "success"
            );

            applyFilters();
        } catch (error) {
            console.error(error);

            button.textContent =
                button.dataset.previousText ||
                "Mark Posted";

            button.disabled =
                false;

            showMessage(
                postId,
                error.message ||
                    "Unable to mark response as posted.",
                "error"
            );
        } finally {
            setButtonLoading(
                button,
                false
            );
        }
    }


    function applyFilters() {
        const query =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";

        const selectedStatus =
            statusFilter
                ? statusFilter.value
                : "all";

        let visibleCount = 0;

        postCards.forEach(
            (card) => {
                const searchText =
                    card.dataset.searchText ||
                    "";

                const cardStatus =
                    card.dataset.status ||
                    "no-response";

                const matchesSearch =
                    !query ||
                    searchText.includes(
                        query
                    );

                const matchesStatus =
                    selectedStatus ===
                        "all" ||
                    cardStatus ===
                        selectedStatus;

                const visible =
                    matchesSearch &&
                    matchesStatus;

                card.hidden =
                    !visible;

                if (visible) {
                    visibleCount += 1;
                }
            }
        );

        if (emptyState) {
            emptyState.hidden =
                visibleCount !== 0;
        }
    }


    document
        .querySelectorAll(
            ".generate-button"
        )
        .forEach(
            (button) => {
                button.addEventListener(
                    "click",
                    () => {
                        const postId =
                            button.dataset
                                .postId;

                        generateResponse(
                            postId,
                            button
                        );
                    }
                );
            }
        );


    document
        .querySelectorAll(
            ".copy-button"
        )
        .forEach(
            (button) => {
                button.addEventListener(
                    "click",
                    () => {
                        const postId =
                            button.dataset
                                .postId;

                        handleCopy(
                            postId
                        );
                    }
                );
            }
        );


    document
        .querySelectorAll(
            ".linkedin-button"
        )
        .forEach(
            (button) => {
                button.addEventListener(
                    "click",
                    () => {
                        const postId =
                            button.dataset
                                .postId;

                        const postUrl =
                            button.dataset
                                .postUrl;

                        handleCopyAndOpen(
                            postId,
                            postUrl
                        );
                    }
                );
            }
        );


    document
        .querySelectorAll(
            ".posted-button"
        )
        .forEach(
            (button) => {
                /*
                 * Cards rendered from the server may
                 * already be in the posted state.
                 */
                if (
                    button.disabled &&
                    button.textContent
                        .trim()
                        .startsWith(
                            "Posted"
                        )
                ) {
                    button.dataset.posted =
                        "true";
                } else {
                    button.dataset.posted =
                        "false";
                }

                button.addEventListener(
                    "click",
                    () => {
                        const postId =
                            button.dataset
                                .postId;

                        markPosted(
                            postId,
                            button
                        );
                    }
                );
            }
        );


    if (searchInput) {
        searchInput.addEventListener(
            "input",
            applyFilters
        );
    }


    if (statusFilter) {
        statusFilter.addEventListener(
            "change",
            applyFilters
        );
    }


    applyFilters();
});