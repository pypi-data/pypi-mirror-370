from squirro_client.exceptions import NotFoundError, UnknownError


class SuggestImageMixin:
    def suggest_images(self, project_id, term, num_suggestions=15):
        """
        Returns image url suggestions relevant to a term
        :param project_id: Project Identifier
        :param term: Term for image suggestion
        :param num_suggestions: number of suggested image urls

        Example::

            >>> client.suggest_images('Xh9CeyQtTYe2cv5F11e6nQ', 'apple', num_suggestions=2)
            [
                'https://images.pexels.com/photos/3652898/pexels-photo-3652898.jpeg?auto=compress&cs=tinysrgb&h=350', 'https://images.pexels.com/photos/4065876/pexels-photo-4065876.jpeg?auto=compress&cs=tinysrgb&h=350'
            ]
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/images/suggest_images"

        params = {"term": term, "num_suggestions": num_suggestions}
        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def retrieve_image(self, project_id, image_url):
        """
        Returns image in byte format for an image_url
        :param project_id: Project Identifier
        :param image_url: url of an image

         Example::
            >>> client.retrieve_image('Xh9CeyQtTYe2cv5F11e6nQ', 'https://images.pexels.com/photos/3652898/pexels-photo-3652898.jpeg?auto=compress&cs=tinysrgb&h=350')
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/images/retrieve_image"

        params = {"image_url": image_url}
        res = self._perform_request("get", url, params=params)
        if res.status_code == 404:
            raise NotFoundError(res.status_code, "Requested image not found")
        elif res.status_code != 200:
            raise UnknownError(res.status_code, "")
        return res.content
