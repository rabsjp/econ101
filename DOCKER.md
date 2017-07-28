Build the image:

```
> sudo docker build .
  ...
  Successfully built a59a280b4c46
```

Tag the image:

```
> sudo docker tag a59a280b4c46 leepslab/otree
```

Bring up the tagged container:

```
> sudo docker-compose up
```